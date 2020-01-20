from logging import getLogger
from datetime import datetime
from pathlib import Path
from sqlite3 import OperationalError, connect, IntegrityError
from json import load

lg = getLogger(__name__)

SQL_TABLES = Path(__file__).parent / 'tables.json'

with SQL_TABLES.open() as f:
    TABLES = load(f)

def open_database(path_to_database):
    sql = connect(str(path_to_database))

    cur = sql.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    return sql, cur


def list_subjects(cur):
    cur.execute(f"SELECT code FROM subjects ORDER BY id")
    return [Subject(cur, x[0]) for x in cur.fetchall()]


class Table():
    t = ''
    columns = []
    subtables = {}

    def __init__(self, cur, id):
        self.id = id
        self.cur = cur
        self.columns = columns(self.t)
        self.subtables = construct_subtables(self.t)

    def __str__(self):
        return f'<{self.t} (#{self.id})>'

    def __repr__(self):
        return f'{self.t.capitalize()}(cur, id={self.id})'

    def __eq__(self, other):
        """So that we can compare instances very easily with set"""
        return self.t == other.t and self.id == other.id

    def __hash__(self):
        """So that we can compare instances very easily with set"""
        return hash(self.__str__())

    def delete(self):
        self.cur.execute(f"""\
            DELETE FROM {self.t}s WHERE id == {self.id}
            """)
        self.id = None
        self.cur = None

    def __getattr__(self, key):

        if key in self.subtables:
            table_name = self.subtables[key]
            id_name = f'{self.t}_id'

        else:
            table_name = f'{self.t}s'
            id_name = 'id'

        self.cur.execute(f"SELECT {key} FROM {table_name} WHERE {id_name} == {self.id}")
        out = self.cur.fetchone()

        if out is None:
            return None

        else:
            out = out[0]

        if key.startswith('date_of_'):
            return _date_out(out)

        elif key.endswith('_time'):
            return _datetime_out(out)

        else:
            return out

    def __setattr__(self, key, value):

        BUILTINS = (
            'cur',
            'id',
            't',
            'code',
            'columns',
            'subtables',
            '__class__',
            'experimenters',
            'subject',
            'session',
            'run',
            )

        if key in BUILTINS:
            super().__setattr__(key, value)
            return

        if key in self.subtables:
            table_name = self.subtables[key]
            id_name = f'{self.t}_id'

        else:
            table_name = f'{self.t}s'
            id_name = 'id'

        if key.startswith('date_of_'):
            value = _date(value)
        elif key.endswith('time'):
            value = _datetime(value)
        else:
            value = _null(value)

        try:  # create record id if it does not exist
            self.cur.execute(f"""\
                INSERT INTO {table_name} ("{id_name}")
                VALUES ("{self.id}")
                """)

        except IntegrityError:
            pass

        try:
            self.cur.execute(f"""\
                UPDATE {table_name}
                SET "{key}"={value}
                WHERE {id_name} == "{self.id}"
                """)

        except (OperationalError, IntegrityError) as err:
            lg.warning(f'{str(err)} when setting {key}={value} for {self}')


class Table_with_files(Table):

    def list_files(self):
        self.cur.execute(f"SELECT file_id FROM {self.t}s_files WHERE {self.t}_id == {self.id}")
        return [File(self.cur, x[0]) for x in self.cur.fetchall()]

    def add_file(self, format, path):
        path = Path(path).resolve()

        self.cur.execute(f"SELECT id, format FROM files WHERE path == '{path}'")
        file_row = self.cur.fetchone()

        if file_row is not None:
            file_id, format_in_table = file_row

            if format != format_in_table:
                raise ValueError(f'Input format "{format}" does not match the format "{format_in_table}" in the table for {path}')

        else:
            self.cur.execute(f"""\
            INSERT INTO files ("format", "path")
            VALUES ("{format}", "{path.resolve()}")""")
            self.cur.execute("""SELECT last_insert_rowid()""")
            file_id = self.cur.fetchone()[0]

        self.cur.execute(f"""INSERT INTO {self.t}s_files ("{self.t}_id", "file_id") VALUES ({self.id}, {file_id})""")


class File(Table):
    t = 'file'

    def __init__(self, cur, id):
        super().__init__(cur, id)

    @property
    def path(self):
        self.cur.execute(f"SELECT path FROM files WHERE id == {self.id}")
        return Path(self.cur.fetchone()[0]).resolve()


class Recording(Table_with_files):
    t = 'recording'
    run = None

    def __init__(self, cur, id, run=None):
        self.run = run
        super().__init__(cur, id)


class Run(Table_with_files):
    t = 'run'
    session = None

    def __init__(self, cur, id, session=None):
        self.session = session
        super().__init__(cur, id)

    def __str__(self):
        return f'<{self.t} (#{self.id})>'

    def list_recordings(self):
        self.cur.execute(f"""\
        SELECT recordings.id FROM recordings
        WHERE recordings.run_id == {self.id}""")
        return [Recording(self.cur, x[0], run=self) for x in self.cur.fetchall()]

    def add_recording(self, modality, offset=0):

        self.cur.execute(f"""\
        INSERT INTO recordings ("run_id", "modality", "offset")
        VALUES ("{self.id}", "{modality}", "{offset}")""")
        self.cur.execute("""SELECT last_insert_rowid()""")
        recording_id = self.cur.fetchone()[0]

        recording = Recording(self.cur, recording_id)
        recording.run = self

        return recording

    @property
    def experimenters(self):
        self.cur.execute(f"""\
            SELECT name FROM experimenters
            JOIN runs_experimenters ON experimenters.id == runs_experimenters.experimenter_id
            WHERE run_id == {self.id}""")
        return [x[0] for x in self.cur.fetchall()]

    @experimenters.setter
    def experimenters(self, experimenters):
        """TODO: probably we should delete the previous pairs"""
        for exp in experimenters:
            self.cur.execute(f'SELECT id FROM experimenters WHERE name == "{exp}"')
            exp_id = self.cur.fetchone()
            if exp_id is None:
                lg.warning(f'Could not find Experimenter called "{exp}". You should add it to "Experimenters" table')
                continue
            else:
                exp_id = exp_id[0]
            self.cur.execute(f"""\
                INSERT INTO runs_experimenters ("run_id", "experimenter_id")
                VALUES ("{self.id}", "{exp_id}")""")


class Protocol(Table_with_files):
    t = 'protocol'

    def __init__(self, cur, id):
        super().__init__(cur, id)


class Channels(Table):
    t = 'channel'

    def __init__(self, cur, id):
        super().__init__(cur, id)


class Electrodes(Table):
    t = 'electrode'

    def __init__(self, cur, id):
        super().__init__(cur, id)


class Session(Table_with_files):
    t = 'session'
    subject = None

    def __init__(self, cur, id, subject=None):
        super().__init__(cur, id)
        self.subject = subject

    def __str__(self):
        return f'<{self.t} {self.name} (#{self.id})>'

    @property
    def start_time(self):
        self.cur.execute(f"""\
            SELECT MIN(runs.start_time) FROM runs WHERE runs.session_id == {self.id}
            """)
        return _datetime_out(self.cur.fetchone()[0])

    @property
    def end_time(self):
        self.cur.execute(f"""\
            SELECT MAX(runs.end_time) FROM runs WHERE runs.session_id == {self.id}
            """)
        return _datetime_out(self.cur.fetchone()[0])

    def list_runs(self):
        self.cur.execute(f"""\
        SELECT runs.id FROM runs
        WHERE runs.session_id == {self.id}""")
        return [Run(self.cur, x[0], session=self) for x in self.cur.fetchall()]

    def add_run(self, task_name, start_time, end_time):

        self.cur.execute(f"""\
        INSERT INTO runs ("session_id", "task_name", "start_time", "end_time")
        VALUES ("{self.id}", "{task_name}", "{start_time}", "{end_time}")""")
        self.cur.execute("""SELECT last_insert_rowid()""")
        run_id = self.cur.fetchone()[0]

        run = Run(self.cur, run_id)
        run.session = self

        return run

    def add_protocol(self, METC, date_of_signature=None):

        if isinstance(METC, str):
            self.cur.execute(f"""\
            INSERT INTO protocols ("METC", "date_of_signature")
            VALUES ("{METC}", {_date(date_of_signature)})""")
            self.cur.execute("""SELECT last_insert_rowid()""")
            protocol_id = self.cur.fetchone()[0]

        else:
            protocol_id = METC.id

        self.cur.execute(f"""\
            INSERT INTO sessions_protocols ("session_id", "protocol_id") VALUES ({self.id}, {protocol_id})""")

        protocol = Protocol(self.cur, protocol_id)

        return protocol

    def list_protocols(self):
        self.cur.execute(f"""\
        SELECT protocol_id FROM sessions_protocols
        WHERE session_id == {self.id}""")
        return [Protocol(self.cur, x[0]) for x in self.cur.fetchall()]


class Subject(Table_with_files):
    t = 'subject'

    def __init__(self, cur, code=None, id=None):

        if code is not None:
            self.code = code
            cur.execute(f"SELECT id FROM subjects WHERE code == '{code}'")
            output = cur.fetchone()
            if output is None:
                raise ValueError(f'There is no "{code}" in "subjects" table')

            else:
                id = output[0]

        super().__init__(cur, id)

        if code is None:
            self.code = self.__getattr__('code')  # explicit otherwise it gets ignored

    def list_sessions(self):
        self.cur.execute(f"""\
        SELECT sessions.id, name FROM sessions
        WHERE sessions.subject_id ==  '{self.id}'""")
        return [Session(self.cur, x[0], subject=self) for x in self.cur.fetchall()]

    def add_session(self, name):

        self.cur.execute(f"""\
        INSERT INTO sessions ("subject_id", "name")
        VALUES ("{self.id}", "{name}")""")
        self.cur.execute("""SELECT last_insert_rowid()""")
        session_id = self.cur.fetchone()[0]

        sess = Session(self.cur, session_id)
        sess.subject = self

        return sess

    @classmethod
    def add(cls, cur, code, date_of_birth=None, sex=None):

        cur.execute(f"""\
            INSERT INTO subjects ("code", "date_of_birth", "sex")
            VALUES ("{code}", {_date(date_of_birth)}, {_null(sex)})""")
        return Subject(cur, code)


def columns(t):
    return [x for x in TABLES[t + 's'] if not x.endswith('id') and x != 'subtables']


def construct_subtables(t):
    if 'subtables' not in TABLES[t + 's']:
        return {}
    else:
        subtables = TABLES[t + 's']['subtables']

    attr_tables = {}
    for k, v in subtables.items():
        for i_v in v:
            if i_v.endswith('_id'):
                continue
            attr_tables[i_v] = k

    return attr_tables


def _null(s):
    if s is None:
        return 'null'
    else:
        return f'"{s}"'


def _date(s):
    if s is None:
        return 'null'
    else:
        return f'"{s:%Y-%m-%d}"'


def _datetime(s):
    if s is None:
        return 'null'
    else:
        return f'"{s:%Y-%m-%d %H:%M:%S}"'


def _date_out(s):
    if s is None:
        return None
    else:
        return datetime.strptime(s, '%Y-%m-%d').date()


def _datetime_out(s):
    if s is None:
        return None
    else:
        return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
