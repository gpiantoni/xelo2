"""Subtables should have a field called "when" and be called "parents_EXTRA"
"""
from logging import getLogger

from PyQt5.QtSql import (
    QSqlDatabase,
    )

from .tables import parse_subtables, LEVELS


lg = getLogger(__name__)


def access_database(db_name, username=None, password=None):

    db = open_database(db_name, username=username, password=password, connectionName='xelo2_database')
    info_schema = open_database('information_schema', username=username, password=password, connectionName='info')

    subtables = []
    for table in LEVELS:
        subtables.extend(parse_subtables(info_schema, db, table))

    return {
        'db': db,
        'info': info_schema,
        'tables': tables,
        'subtables': subtables,
        }


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
