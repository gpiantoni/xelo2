from xelo2.database.create import create_database, open_database
from PyQt5.QtSql import QSql

from .paths import DB_ARGS


def test_create():
    create_database(**DB_ARGS)
    if DB_ARGS['db_type'] == 'QSQLITE':
        assert DB_ARGS['db_name'].exists()

def test_open():
    db = open_database(**DB_ARGS)
    if DB_ARGS['db_type'] == 'QSQLITE':
        n_tables = 34  # extra system tables in SQLITE
    else:
        n_tables = 32
    assert len(db.tables(QSql.AllTables)) == n_tables
