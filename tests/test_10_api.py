from pytest import raises

from xelo2.database.create import open_database
from xelo2.api import Subject, list_subjects

from .paths import DB_PATH


def test_api_subject():
    open_database(DB_PATH)

    subj = Subject.add('subject_test')
    assert subj.id == 1
    assert str(subj) == '<subject (#1)>'
    assert repr(subj) == 'Subject(code="subject_test")'

    with raises(ValueError):
        Subject.add('subject_test')

    with raises(ValueError):
        Subject('does_not_exist')

    subj_copy = Subject('subject_test')

    assert subj == subj_copy
    assert len({subj, subj_copy}) == 1


def test_api_session():

    subj = list_subjects()[0]
    sess = subj.add_session('MRI')

    assert sess.id == 1
    assert str(sess) == '<session MRI (#1)>'
    assert repr(sess) == 'Session(id=1)'
    assert sess.subject == subj


def test_api_run():
    subj = list_subjects()[0]
    sess = subj.list_sessions()[0]

    run = sess.add_run('motor')
    assert str(run) == '<run "motor" (#1)>'
    assert repr(run) == 'Run(id=1)'
    assert run.session == sess
