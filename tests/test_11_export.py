from xelo2.database.create import open_database, close_database
from xelo2.io.export_db import export_database
from xelo2.io.import_db import import_database
from xelo2.api import list_subjects

from numpy import empty, lexsort, where, genfromtxt
from numpy.testing import assert_array_equal

from .paths import DB_ARGS, EXPORT_0, EXPORT_1, DB_EXPORT, TRC_PATH


def test_import_export():
    db = open_database(**DB_ARGS)

    if True:
        _add_items(db)  # add some random elements to test import and export
    export_database(db, EXPORT_0)
    close_database(db)

    import_database(EXPORT_0, **DB_EXPORT)

    db = open_database(**DB_EXPORT)
    export_database(db, EXPORT_1)
    close_database(db)

    _compare_tables(EXPORT_0, EXPORT_1)


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
        n_lines_0 = sum(1 for line in f)

    with PATH_1.open() as f:
        n_lines_1 = sum(1 for line in f)
    assert n_lines_0 == n_lines_1

    t0 = genfromtxt(PATH_0, delimiter='\t', dtype='U', encoding='utf8')
    if t0.ndim == 1:
        t0 = t0[None, :]
    t1 = genfromtxt(PATH_1, delimiter='\t', dtype='U', encoding='utf8')
    if t1.ndim == 1:
        t1 = t1[None, :]

    assert_array_equal(t0[0, :], t1[0, :])
    header = t0[0, :]

    # ignore id columns
    cols = [i for i, h in enumerate(header) if not h.endswith('id') and not h == 'electrode_groups.IntendedFor']

    X0 = _sort(t0[1:, cols])
    X1 = _sort(t1[1:, cols])

    # find which columns are not in agreement
    bad_cols = where((X0 != X1).sum(axis=0) > 0)[0]

    error = []
    for bad_col in bad_cols:
        error.append(header[cols][bad_col])
        bad_values = X0[:, bad_col] != X1[:, bad_col]
        error.append(', '.join(X0[bad_values, bad_col]))
        error.append(', '.join(X1[bad_values, bad_col]))

    if error:
        raise ValueError('\n'.join(error))


def _sort(X):
    return X[lexsort(X.T), :]
