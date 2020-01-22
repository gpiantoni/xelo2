from pytest import raises

from xelo2.database.create import open_database
from xelo2.api import Subject

from .paths import DB_PATH


def test_api_subj():
    open_database(DB_PATH)

    subj = Subject.add('subject_test')
    assert subj.id == 1

    with raises(ValueError):
        Subject.add('subject_test')

    with raises(ValueError):
        Subject('does_not_exist')

    subj_copy = Subject('subject_test')

    assert subj == subj_copy

