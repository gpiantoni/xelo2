from xelo2.database.create import open_database
from xelo2.io.export_db import export_database
from xelo2.io.import_db import import_database
from xelo2.api import list_subjects

from numpy import empty

from .paths import DB_ARGS, EXPORT_0, EXPORT_1, DB_EXPORT, TRC_PATH


def test_import_export():
    db = open_database(**DB_ARGS)

    _add_items(db)  # add some random elements to test import and export
    export_database(db, EXPORT_0)

    import_database(EXPORT_0, **DB_EXPORT)
    export_database(db, EXPORT_1)

    _compare_tables(EXPORT_0, EXPORT_1)
    db.close()


def _add_items(db):
    subj = list_subjects(db)[2]
    subj.add_file('micromed', TRC_PATH)

    sess = subj.list_sessions()[0]
    run = sess.list_runs()[0]

    events = run.events
    events = empty(5, dtype=events.dtype)
    events['onset'] = range(5)
    events['duration'] = 2
    events['trial_type'] = 'test 2'
    run.events = events


def _compare_tables(PATH_0, PATH_1):
    for name in PATH_0.glob('*.tsv'):
        _compare_table(name, PATH_1 / name.name)


def _compare_table(PATH_0, PATH_1):
    """It does not check id values (because they might differ across tables).
    This has the side effect that you cannot see if tables are linked correctly.
    """
    with PATH_0.open() as f:
        n_lines_0 = sum(1 for l in f)

    with PATH_1.open() as f:
        n_lines_1 = sum(1 for l in f)
    assert n_lines_0 == n_lines_1

    with PATH_0.open() as f0, PATH_1.open() as f1:
        header = f0.readline()[:-1].split('\t')
        header = f1.readline()[:-1].split('\t')
        print(header)
        id_codes = [i for i, h in enumerate(header) if h.endswith('id') or h == 'electrode_groups.IntendedFor']

        for l0, l1 in zip(f0, f1):
            l0 = l0[:-1].split('\t')
            l1 = l1[:-1].split('\t')
            different = [i for i, (v0, v1) in enumerate(zip(l0, l1)) if v0 != v1 and i not in id_codes]
            assert len(different) == 0
