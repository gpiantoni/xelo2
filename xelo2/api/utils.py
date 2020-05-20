from logging import getLogger
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
