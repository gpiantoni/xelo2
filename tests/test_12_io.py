from xelo2.api.structure import Subject
from xelo2.io.tsv import save_tsv, load_tsv
from xelo2.io.parrec import add_parrec_to_sess

from .paths import TSV_PATH, T1_PATH


def test_export_events():

    subj = Subject('subject_test')
    sess = subj.list_sessions()[0]
    run = sess.list_runs()[0]
    X = run.events

    save_tsv(TSV_PATH, X)

    load_tsv(TSV_PATH, X.dtype)


def test_import_parrec():
    subj = Subject('subject_test')
    sess = subj.list_sessions()[0]
    n_runs = len(sess.list_runs())
    add_parrec_to_sess(sess, T1_PATH)
    assert len(sess.list_runs()) == n_runs + 1
