from logging import getLogger
from datetime import datetime
from PyQt5.QtSql import QSqlQuery

lg = getLogger(__name__)


def find_subject_id(db, code):
    query = QSqlQuery(db)
    query.prepare('SELECT subject_id FROM subject_codes WHERE subject_codes.code = :code')
    query.bindValue(':code', code)

    if query.exec():
        if query.next():
            return query.value('subject_id')
        else:
            return None

    else:
        lg.warning(query.lastError().text())


def sort_subjects_alphabetical(subj):
    return str(subj)


def sort_subjects_date(subj):
    sessions = subj.list_sessions()
    if len(sessions) == 0 or sessions[0].start_time is None:
        return datetime(1900, 1, 1, 0, 0, 0)
    else:
        return sessions[0].start_time


def sort_sessions_starttime(obj):
    if obj.start_time is None:
        return datetime.now()
    else:
        return obj.start_time
