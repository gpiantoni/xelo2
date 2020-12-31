from xelo2.database.open_db import open_database

from .paths import DB_ARGS


def test_open(qtbot):
    db = open_database(**DB_ARGS)
    n_tables = 32
    assert len(db.tables()) == n_tables
