from xelo2.database.create import create_database, open_database

from .paths import DB_PATH


def test_create():
    create_database(DB_PATH)
    assert DB_PATH.exists()


def test_open():
    db = open_database(DB_PATH)
    assert len(db.tables()) == 26
