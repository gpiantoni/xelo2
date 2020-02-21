from numpy import genfromtxt
from numpy import floating, character, issubdtype, isnan
from numpy.lib.recfunctions import rename_fields


def load_tsv(fname, dtypes):
    X = genfromtxt(
        fname,
        dtype=dtypes,
        skip_header=1,
        delimiter='\t'
        )
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
