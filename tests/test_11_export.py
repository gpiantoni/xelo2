
def _compare_tables():
    with open(export_dir / 'sql_test2.tsv') as f1, open(export_dir / 'sql_test.tsv') as f0:
        header = f0.readline()[:-1].split('\t')
        header = f1.readline()[:-1].split('\t')
        id_codes = [i for i, h in enumerate(header) if h.endswith('id')]

        for l0, l1 in zip(f0, f1):
            l0 = l0[:-1].split('\t')
            l1 = l1[:-1].split('\t')
            different = [i for i, (v0, v1) in enumerate(zip(l0, l1)) if v0 != v1 and i not in id_codes]
            assert len(different) == 0
