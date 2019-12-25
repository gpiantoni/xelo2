from datetime import datetime
from pathlib import Path
from sqlite3 import OperationalError, connect


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

    def __init__(self, cur, id):
        self.id = id
        self.cur = cur

    def __repr__(self):
        return f'<{self.t} (#{self.id})>'

    def __eq__(self, other):
        """So that we can compare instances very easily with set"""
        return self.t == other.t and self.id == other.id

    def __hash__(self):
        """So that we can compare instances very easily with set"""
        return hash(self.__repr__())

    def __getattr__(self, key, table_name=None):

        if table_name is None:
            table_name = f'{self.t}s'
            id_name = 'id'

        else:
            id_name = f'{self.t}_id'

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

        if key in ('cur', 'id', 't', 'code'):
            super().__setattr__(key, value)
            return

        if key.startswith('date_of_'):
            value = _date(value)
        elif key.endswith('time'):
            value = _datetime(value)
        else:
            value = _null(value)

        self.cur.execute(f"UPDATE {self.t}s SET {key} = {value} WHERE id == {self.id}")


class Table_with_files(Table):

    def list_files(self):
        self.cur.execute(f"SELECT file_id FROM {self.t}s_files WHERE {self.t}_id == {self.id}")
        return [File(self.cur, x[0]) for x in self.cur.fetchall()]

    def add_file(self, format, path):
        path = Path(path)
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

    def __init__(self, cur, id):
        super().__init__(cur, id)


class Run(Table_with_files):
    t = 'run'

    def __init__(self, cur, id):
        super().__init__(cur, id)

    def __repr__(self):
        return f'<{self.t} {self.acquisition} (#{self.id})>'

    def list_recordings(self):
        self.cur.execute(f"""\
        SELECT recordings.id FROM recordings
        WHERE recordings.run_id == {self.id}""")
        return [Recording(self.cur, x[0]) for x in self.cur.fetchall()]

    def add_recording(self, modality, offset=0):

        self.cur.execute(f"""\
        INSERT INTO recordings ("run_id", "modality", "offset")
        VALUES ("{self.id}", "{modality}", "{offset}")""")
        self.cur.execute("""SELECT last_insert_rowid()""")
        recording_id = self.cur.fetchone()[0]

        return Recording(self.cur, recording_id)


class Protocol(Table_with_files):
    t = 'protocol'

    def __init__(self, cur, id):
        self.id = id
        self.cur = cur


class Session(Table_with_files):
    t = 'session'

    def __init__(self, cur, id):
        self.id = id
        self.cur = cur

    def __repr__(self):
        return f'<{self.t} {self.name} (#{self.id})>'

    @property
    def start_date(self):
        self.cur.execute(f"""\
            SELECT MIN(runs.start_time) FROM runs WHERE runs.session_id == {self.id}
            """)
        return self.cur.fetchone()[0]

    @property
    def end_date(self):
        self.cur.execute(f"""\
            SELECT MAX(runs.end_time) FROM runs WHERE runs.session_id == {self.id}
            """)
        return self.cur.fetchone()[0]

    def __getattr__(self, key):

        if key in ('date_of_surgery', ):
            return super().__getattr__(key, 'sessions_or')

        elif key in ('date_of_implantation', 'date_of_explantation'):
            return super().__getattr__(key, 'sessions_iemu')

        else:
            return super().__getattr__(key)

    def __setattrx__(self, key, value):
        """When changing name, then you need to delete the unused table
        """
        pass

    def list_runs(self):
        self.cur.execute(f"""\
        SELECT runs.id FROM runs
        WHERE runs.session_id == {self.id}""")
        return [Run(self.cur, x[0]) for x in self.cur.fetchall()]

    def add_run(self, task_name, acquisition, start_time, end_time):

        self.cur.execute(f"""\
        INSERT INTO runs ("session_id", "task_name", "acquisition", "start_time", "end_time")
        VALUES ("{self.id}", "{task_name}", "{acquisition}", "{start_time}", "{end_time}")""")
        self.cur.execute("""SELECT last_insert_rowid()""")
        run_id = self.cur.fetchone()[0]

        return Run(self.cur, run_id)

    def add_protocol(self, METC, version=None, date_of_signature=None):

        if isinstance(METC, str):
            self.cur.execute(f"""\
            INSERT INTO protocols ("METC", "version", "date_of_signature")
            VALUES ("{METC}", {_null(version)}, {_date(date_of_signature)})""")
            self.cur.execute("""SELECT last_insert_rowid()""")
            protocol_id = self.cur.fetchone()[0]

        else:
            protocol_id = METC.id

        self.cur.execute(f"""\
            INSERT INTO sessions_protocols ("session_id", "protocol_id") VALUES ({self.id}, {protocol_id})""")
        return Protocol(self.cur, protocol_id)

    def list_protocols(self):
        self.cur.execute(f"""\
        SELECT protocol_id FROM sessions_protocols
        WHERE session_id == {self.id}""")
        return [Protocol(self.cur, x[0]) for x in self.cur.fetchall()]


class Subject(Table_with_files):
    t = 'subject'

    def __init__(self, cur, code):
        self.cur = cur
        self.code = code
        cur.execute(f"SELECT id FROM subjects WHERE code == '{code}'")
        output = cur.fetchone()
        if output is None:
            raise ValueError(f'There is no "{code}" in "subjects" table')

        else:
            self.id = output[0]

    def list_sessions(self):
        self.cur.execute(f"""\
        SELECT sessions.id, name FROM sessions
        WHERE sessions.subject_id ==  '{self.id}'""")
        return [Session(self.cur, x[0]) for x in self.cur.fetchall()]

    def add_session(self, name, **kwargs):

        self.cur.execute(f"""\
        INSERT INTO sessions ("subject_id", "name")
        VALUES ("{self.id}", "{name}")""")
        self.cur.execute("""SELECT last_insert_rowid()""")
        session_id = self.cur.fetchone()[0]

        if name == 'IEMU':
            self.cur.execute(f"""\
            INSERT INTO sessions_iemu (
                "session_id",
                "date_of_implantation",
                "date_of_explantation")
            VALUES (
                "{session_id}",
                {_date(kwargs['date_of_implantation'])},
                {_date(kwargs['date_of_explantation'])}
                )""")

        elif name == 'OR':
            self.cur.execute(f"""\
            INSERT INTO sessions_or (
                "session_id",
                "date_of_surgery")
            VALUES (
                "{session_id}",
                {_date(kwargs['date_of_surgery'])}
                )""")

        return Session(self.cur, session_id)

    @classmethod
    def add(cls, cur, code, date_of_birth=None, sex=None):

        cur.execute(f"""\
            INSERT INTO subjects ("code", "date_of_birth", "sex")
            VALUES ("{code}", {_date(date_of_birth)}, {_null(sex)})""")
        return Subject(cur, code)


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
