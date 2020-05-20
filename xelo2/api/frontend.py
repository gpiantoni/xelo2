from logging import getLogger
from PyQt5.QtSql import QSqlQuery

from .backend import Table_with_files
from .utils import find_subject_id

lg = getLogger(__name__)


def list_subjects(db, alphabetical=False, reverse=False):
    """List of the subjects in the currently open database, sorted based on
    the date of their first run.

    Parameters
    ----------
    alphabetical : bool
        False -> sort by date of first run
        True -> sort alphabetically

    reverse : bool
        False -> oldest to newest, True -> newest to oldest
        False -> A to Z, True -> Z to A

    Returns
    -------
    list of instances of Subject
        list of subjects in the database
    """
    query = QSqlQuery("SELECT id FROM subjects")

    list_of_subjects = []
    while query.next():
        list_of_subjects.append(Subject(id=query.value('id')))

    if alphabetical:
        _sort_subjects = _sort_subjects_alphabetical
    else:
        _sort_subjects = _sort_subjects_date

    return sorted(list_of_subjects, key=_sort_subjects, reverse=reverse)


class Subject(Table_with_files):
    t = 'subject'

    def __init__(self, db, code=None, id=None):
        if code is not None:
            id = find_subject_id(db, code)
            if id is None:
                raise ValueError(f'There is no "{code}" in "subject_codes" table')

        super().__init__(db, id)

    def __str__(self):
        codes = self.codes
        if len(codes) == 0:
            return '(subject without code)'
        elif len(codes) == 1:
            return codes[0]
        else:
            return ', '.join(codes)

    @classmethod
    def add(cls, db, code):
        """You can create an empty subject, with no code, but it's a bad idea
        """
        id = find_subject_id(db, code)
        if id is not None:
            raise ValueError(f'Subject "{code}" already exists')

        # add empty value to get new id
        query = QSqlQuery(db)
        query.prepare("INSERT INTO subjects (`sex`) VALUES (NULL) ")
        if query.exec():
            id = query.lastInsertId()
        else:
            raise ValueError(query.lastError().text())

        query = QSqlQuery(db)
        query.prepare("INSERT INTO subject_codes (`subject_id`, `code`) VALUES (:subject_id, :code)")
        query.bindValue(':subject_id', id)
        query.bindValue(':code', code)
        if query.exec():
            return Subject(db, id=id)

        else:
            raise ValueError(query.lastError().text())

    @property
    def codes(self):
        """Get the codes associated with this subjects"""
        query = QSqlQuery(self.db)
        query.prepare("SELECT code FROM subject_codes WHERE subject_codes.subject_id = :id")
        query.bindValue(':id', self.id)
        if not query.exec():
            lg.warning(query.lastError().text())

        list_of_codes = []
        while query.next():
            list_of_codes.append(query.value('code'))

        # put RESP at the end
        list_of_codes.sort()
        list_of_codes.sort(key=lambda s: s.startswith('RESP'))
        return list_of_codes

    @codes.setter
    def codes(self, codes):

        query = QSqlQuery(self.db)
        query.prepare('DELETE FROM subject_codes WHERE subject_id = :id')
        query.bindValue(':id', self.id)
        if not query.exec():
            lg.warning(query.lastError().text())

        query = QSqlQuery(self.db)
        query.prepare("INSERT INTO subject_codes (`subject_id`, `code`) VALUES (:id, :code)")
        query.bindValue(':id', self.id)
        for code in set(codes):
            query.bindValue(':code', code)
            if not query.exec():
                raise ValueError(query.lastError().text())

    def add_session(self, name):

        query = QSqlQuery(f"""\
            INSERT INTO sessions (`subject_id`, `name`)
            VALUES ("{self.id}", "{name}")""")

        session_id = query.lastInsertId()
        if session_id is None:
            err = query.lastError()
            raise ValueError(err.text())

        return Session(session_id, subject=self)

    def list_sessions(self):
        query = QSqlQuery(f"""\
            SELECT sessions.id, name FROM sessions
            WHERE sessions.subject_id =  '{self.id}'""")

        list_of_sessions = []
        while query.next():
            list_of_sessions.append(
                Session(
                    id=query.value('id'),
                    subject=self))
        return sorted(list_of_sessions, key=_sort_starttime)

    def add_protocol(self, METC, date_of_signature=None):

        query = QSqlQuery(f"""\
            INSERT INTO protocols (`subject_id`, `METC`, `date_of_signature`)
            VALUES ("{self.id}", "{METC}", {_date(date_of_signature)})""")

        protocol_id = query.lastInsertId()
        if protocol_id is None:
            err = query.lastError()
            raise ValueError(err.text())

        return Protocol(protocol_id, subject=self)

    def list_protocols(self):
        query = QSqlQuery(f"""\
            SELECT id FROM protocols WHERE subject_id =  '{self.id}'""")

        list_of_protocols = []
        while query.next():
            list_of_protocols.append(
                Protocol(
                    id=query.value('id'),
                    subject=self))
        return sorted(list_of_protocols, key=lambda obj: obj.METC)

