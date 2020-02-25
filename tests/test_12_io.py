from xelo2.api.structure import Subject
from xelo2.io.tsv import save_tsv, load_tsv

from .paths import TSV_PATH


def test_export_events():

    subj = Subject('subject_test')
    sess = subj.list_sessions()[0]
    run = sess.list_runs()[0]
    X = run.events

    save_tsv(TSV_PATH, X)

    load_tsv(TSV_PATH, X.dtype)
