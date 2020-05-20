from logging import getLogger
from datetime import datetime
from PyQt5.QtSql import QSqlQuery

from numpy import (
    dtype,
    )

from ..database import TABLES

lg = getLogger(__name__)


def construct_subtables(t):
    """For each attribute, this function looks up in which table the information
    is stored.

    Parameters
    ----------
    t : str
        name of the table (subject, session, run, etc)

    Returns
    -------
    dict
        where the key is the attribute and the value is the table
    """
    table = t + 's'
    attr_tables = {}
    for k, v in TABLES.items():
        if not k.startswith(table + '_'):
            continue
        for k0, v0 in v.items():
            if v0 is None or k0 == 'when':
                continue
            attr_tables[k0] = k
    return attr_tables


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


def get_dtypes(table):
    dtypes = []
    for k, v in table.items():
        if v is None:
            continue
        elif v['type'] == 'TEXT':
            dtypes.append((k, 'U4096'))
        elif v['type'] == 'FLOAT':
            dtypes.append((k, 'float'))
        else:
            assert False
    return dtype(dtypes)


def sort_subjects_alphabetical(subj):
    return str(subj)


def sort_subjects_date(subj):
    sessions = subj.list_sessions()
    if len(sessions) == 0 or sessions[0].start_time is None:
        return datetime(1900, 1, 1, 0, 0, 0)
    else:
        return sessions[0].start_time


def sort_starttime(obj):
    if obj.start_time is None:
        return datetime.now()
    else:
        return obj.start_time


def out_date(driver, out):
    if driver == 'QSQLITE':
        if out == '':
            return None
        else:
            return datetime.strptime(out, '%Y-%m-%d').date()
    else:
        raise NotImplementedError('date in MYSQL')


def out_datetime(driver, out):
    if driver == 'QSQLITE':
        if out == '':
            return None
        else:
            return datetime.strptime(out, '%Y-%m-%dT%H:%M:%S')
    else:
        raise NotImplementedError('datetime in MYSQL')
