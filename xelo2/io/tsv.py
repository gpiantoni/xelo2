from collections import defaultdict
from numpy import floating, character, issubdtype, isnan, empty, NaN
from numpy.lib.recfunctions import rename_fields


def load_tsv(fname, dtypes):
    with fname.open() as f:
        header = f.readline().strip().split('\t')
        d = defaultdict(list)
        for l in f:
            values = l.strip().split('\t')
            for h, v in zip(header, values):
                if v == 'n/a':
                    if issubdtype(dtypes[h], floating):
                        v = NaN
                    else:
                        v = ''

                d[h].append(v)

    X = empty(len(d[header[0]]), dtype=dtypes)
    for h in header:
        X[h] = d[h]
    return X


def save_tsv(fname, X):
    # BIDS wants 'group' but it's a reserved word in SQL
    X = rename_fields(X, {'groups': 'group'})
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
