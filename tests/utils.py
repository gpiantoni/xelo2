from pytest import fixture

from xelo2.database.create import open_database

from .paths import DB_PATH


@fixture(scope="package")
def db():
    return open_database(DB_PATH)
