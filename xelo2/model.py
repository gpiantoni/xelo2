from datetime import datetime
from pathlib import Path
from sqlite3 import OperationalError


def list_subjects(cur):
    cur.execute(f"SELECT code FROM subjects")
    return [Subject(cur, x[0]) for x in cur.fetchall()]


class Table():
    t = ''

    def __init__(self, cur, id):
        self.id = id
        self.cur = cur

    def __repr__(self):
        return f'<{self.t} (#{self.id})>'

    @property
    def parameters(self):
        try:
            self.cur.execute(f'SELECT parameter, value FROM {self.t}s_params WHERE {self.t}_id == {self.id} AND value IS NOT ""')

        except OperationalError:  # if table_parameters does not exist
            return {}

        else:
            params = {k: v for k, v in self.cur.fetchall()}
            for k, v in params.items():
                if k.startswith('date_of_'):
                    params[k] = datetime.strptime(v, '%Y-%m-%d').date()
            return params


class Table_with_files(Table):

    def list_files(self):
        self.cur.execute(f"SELECT file_id FROM {self.t}s_files WHERE {self.t}_id == {self.id}")
        return [File(self.cur, x[0]) for x in self.cur.fetchall()]


class File(Table):
    t = 'file'

    def __init__(self, cur, id):
        super().__init__(cur, id)

    @property
    def path(self):
        self.cur.execute(f"SELECT path FROM files WHERE id == {self.id}")
        return Path(self.cur.fetchone()[0]).resolve()

    @property
    def type(self):
        self.cur.execute(f"SELECT type FROM files WHERE id == {self.id}")
        return self.cur.fetchone()[0]


class Recording(Table_with_files):
    t = 'recording'

    def __init__(self, cur, id):
        super().__init__(cur, id)

    @property
    def modality(self):
        self.cur.execute(f"SELECT modality FROM recordings WHERE id == {self.id}")
        return self.cur.fetchone()[0]

    @property
    def start_time(self):
        self.cur.execute(f"SELECT start_time FROM recordings WHERE id == {self.id}")
        t = self.cur.fetchone()[0]
        return datetime.strptime(t, '%Y-%m-%d %H:%M:%S')

    @property
    def end_time(self):
        self.cur.execute(f"SELECT end_time FROM recordings WHERE id == {self.id}")
        t = self.cur.fetchone()[0]
        return datetime.strptime(t, '%Y-%m-%d %H:%M:%S')

class Run(Table_with_files):
    t = 'run'

    def __init__(self, cur, id):
        super().__init__(cur, id)

    @property
    def task_name(self):
        self.cur.execute(f"SELECT task_name FROM runs WHERE id == {self.id}")
        return self.cur.fetchone()[0]

    @property
    def start_time(self):
        self.cur.execute(f"SELECT start_time FROM runs WHERE id == {self.id}")
        t = self.cur.fetchone()[0]
        return datetime.strptime(t, '%Y-%m-%d %H:%M:%S')

    @property
    def end_time(self):
        self.cur.execute(f"SELECT end_time FROM runs WHERE id == {self.id}")
        t = self.cur.fetchone()[0]
        return datetime.strptime(t, '%Y-%m-%d %H:%M:%S')

    def list_recordings(self):
        self.cur.execute(f"""\
        SELECT recordings.id FROM recordings
        JOIN runs ON runs.id == recordings.run_id
        WHERE runs.id == {self.id}""")
        return [Recording(self.cur, x[0]) for x in self.cur.fetchall()]


class Session(Table_with_files):
    t = 'session'

    def __init__(self, cur, id):
        self.id = id
        self.cur = cur

    @property
    def name(self):
        self.cur.execute(f"SELECT session_name FROM sessions WHERE id == {self.id}")
        return self.cur.fetchone()[0]

    def start_date(self):
        pass

    def end_date(self):
        pass

    def list_runs(self):
        self.cur.execute(f"""\
        SELECT runs.id FROM runs
        JOIN sessions ON sessions.id == runs.session_id
        WHERE sessions.id == {self.id}""")
        return [Run(self.cur, x[0]) for x in self.cur.fetchall()]


class Subject(Table_with_files):
    t = 'subject'

    def __init__(self, cur, code):
        self.code = code
        cur.execute(f"SELECT id FROM subjects WHERE code == '{code}'")
        self.id = cur.fetchone()[0]
        self.cur = cur

    @property
    def date_of_birth(self):
        self.cur.execute(f"SELECT date_of_birth FROM subjects WHERE id == '{self.id}'")
        dob = self.cur.fetchone()[0]
        return datetime.strptime(dob, '%Y-%m-%d').date()

    @property
    def sex(self):
        self.cur.execute(f"SELECT sex FROM subjects WHERE id == '{self.id}'")
        return self.cur.fetchone()[0]

    def list_sessions(self):
        self.cur.execute(f"""\
        SELECT sessions.id, session_name FROM sessions
        JOIN subjects ON subjects.id == sessions.subject_id
        WHERE subjects.id == '{self.id}'""")
        return [Session(self.cur, x[0]) for x in self.cur.fetchall()]
