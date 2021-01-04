from xelo2.database.open_db import access_database

from .paths import DB_ARGS


def test_open(qtbot):
    db = access_database(**DB_ARGS)
    n_tables = 25
    assert len(db['db'].tables()) == n_tables
    assert len(db['db'].tables()) == len(db['tables'])
