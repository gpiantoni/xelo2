from collections import defaultdict
from numpy import floating, character, issubdtype, isnan, empty, NaN
from numpy.lib.recfunctions import rename_fields, drop_fields


def load_tsv(fname, dtypes):
    with fname.open() as f:
        header = f.readline().strip().split('\t')
        d = defaultdict(list)
        for line in f:
            values = line.strip('\n').split('\t')
            for h, v in zip(header, values):
                if h == 'group':
                    h = 'groups'
                if v == 'n/a':
                    if issubdtype(dtypes[h], floating):
                        v = NaN
                    else:
                        v = ''

                d[h].append(v)

    X = empty(len(d[header[0]]), dtype=dtypes)
    for h in header:
        if h == 'group':
            h = 'groups'
        X[h] = d[h]
    return X


def save_tsv(fname, X):
    # BIDS wants 'group' but it's a reserved word in SQL
    X = rename_fields(X, {'groups': 'group'})
    X = _remove_empty_columns(X)
    dtypes = X.dtype

    with fname.open('w') as f:
        f.write('\t'.join(dtypes.names) + '\n')

        for x in X:
            values = []
            for name in dtypes.names:

                if issubdtype(dtypes[name], floating):
                    if isnan(x[name]):
                        values.append('n/a')
                    else:
                        values.append(f'{x[name]:.3f}')

                elif issubdtype(dtypes[name], character):
                    if x[name] == '':
                        values.append('n/a')
                    else:
                        values.append(x[name])
            f.write('\t'.join(values) + '\n')


def _remove_empty_columns(tsv):
    """Remove column where all the values are empty (either NaN or '')
    """
    dtypes = tsv.dtype

    to_remove = []
    for name in dtypes.names:

        if issubdtype(dtypes[name], floating):
            if isnan(tsv[name]).all():
                to_remove.append(name)

        elif issubdtype(dtypes[name], character):
            if (tsv[name] == '').all():
                to_remove.append(name)

    return drop_fields(tsv, to_remove)
