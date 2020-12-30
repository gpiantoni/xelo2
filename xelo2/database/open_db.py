"""Subtables should have a field called "when" and be called "parents_EXTRA"
"""
from logging import getLogger
from pathlib import Path

from PyQt5.QtSql import (
    QSqlDatabase,
    QSqlQuery,
    )


lg = getLogger(__name__)
CONNECTION_NAME = 'xelo2_database'


def open_database(db_type, db_name, username=None, password=None, connectionName=CONNECTION_NAME):
    """Open the default database using Qt framework

    Parameters
    ----------
    db_type : str
        driver to use (QSQLITE or QMYSQL)
    db_name : str
        path to database (QSQLITE) or database name (QMYSQL)
    username : str
        user name to open database
    password : str
        password to open database

    Returns
    -------
    QSqlDatabase
        default database
    """
    assert db_type in ('QSQLITE', 'QMYSQL')
    db = QSqlDatabase.addDatabase(db_type, connectionName)
    assert db.isValid()

    if db_type == 'QSQLITE':
        db_name = Path(db_name).expanduser().resolve()
    else:
        db.setHostName('127.0.0.1')
        db.setUserName(username)
        if password is not None:
            db.setPassword(password)

    db.setDatabaseName(str(db_name))
    db.open()

    if db_type == 'QSQLITE':
        assert QSqlQuery(db).exec('PRAGMA foreign_keys = ON;')
        assert QSqlQuery(db).exec('PRAGMA encoding="UTF-8";')

    if not db.isOpen():
        raise ValueError('Could not open database')

    return db


def close_database(db):
    db.close()
    QSqlDatabase.removeDatabase(db.connectionName())
