from xelo2.database.create import open_database
from xelo2.io.export_db import export_database
from xelo2.io.import_db import import_database

from .paths import DB_PATH, EXPORT_0, EXPORT_1, EXPORT_DB


def test_import_export():
    open_database(DB_PATH)
    export_database(EXPORT_0)

    import_database(EXPORT_0, EXPORT_DB)
    export_database(EXPORT_1)

    _compare_tables(EXPORT_0, EXPORT_1)


def _compare_tables(PATH_0, PATH_1):
    for name in PATH_0.glob('*.tsv'):
        _compare_table(name, PATH_1 / name.name)


def _compare_table(PATH_0, PATH_1):

    with PATH_0.open() as f:
        n_lines_0 = sum(1 for l in f)

    with PATH_1.open() as f:
        n_lines_1 = sum(1 for l in f)
    assert n_lines_0 == n_lines_1

    with PATH_0.open() as f0, PATH_1.open() as f1:
        header = f0.readline()[:-1].split('\t')
        header = f1.readline()[:-1].split('\t')
        id_codes = [i for i, h in enumerate(header) if h.endswith('id')]

        for l0, l1 in zip(f0, f1):
            l0 = l0[:-1].split('\t')
            l1 = l1[:-1].split('\t')
            different = [i for i, (v0, v1) in enumerate(zip(l0, l1)) if v0 != v1 and i not in id_codes]
            assert len(different) == 0
