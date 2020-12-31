"""Subtables should have a field called "when" and be called "parents_EXTRA"
"""
from logging import getLogger

from PyQt5.QtSql import (
    QSqlDatabase,
    )

from .tables import parse_all_tables, parse_subtables, LEVELS, EXPECTED_TABLES


lg = getLogger(__name__)


def access_database(db_name, username=None, password=None):

    db = open_database(db_name, username=username, password=password, connectionName='xelo2_database')
    info_schema = open_database('information_schema', username=username, password=password, connectionName='info')

    all_tables = parse_all_tables(info_schema, db)

    subtables = []
    for table in LEVELS:
        subtables.extend(parse_subtables(info_schema, db, table))

    expected_tables = EXPECTED_TABLES + [x['subtable'] for x in subtables]

    remaining_tables = set(all_tables) - set(expected_tables)
    if len(remaining_tables) > 0:
        lg.warning('These tables were not parsed by python API: ' + ', '.join(remaining_tables))

    out = {
        'db': db,
        'info': info_schema,
        'tables': all_tables,
        'subtables': subtables,
        }
    return out


def open_database(db_name, username=None, password=None, connectionName='xelo2_database'):
    """Open the default database using Qt framework

    Parameters
    ----------
    db_name : str
        database name (QMYSQL)
    username : str
        user name to open database
    password : str
        password to open database

    Returns
    -------
    QSqlDatabase
        default database
    """
    db = QSqlDatabase.addDatabase('QMYSQL', connectionName)
    assert db.isValid()

    db.setHostName('127.0.0.1')
    db.setUserName(username)
    if password is not None:
        db.setPassword(password)

    db.setDatabaseName(str(db_name))
    db.open()

    if not db.isOpen():
        raise ValueError('Could not open database')

    return db


def close_database(db):
    db.close()
    QSqlDatabase.removeDatabase(db.connectionName())
