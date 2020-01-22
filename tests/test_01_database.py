from xelo2.database.create import create_database

from .paths import DB_PATH


def test_create():
    create_database(DB_PATH)
    assert DB_PATH.exists()
