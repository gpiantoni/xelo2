from numpy import genfromtxt, savetxt
from .utils import dtype2fmt


def load_tsv(fname, dtypes):
    X = genfromtxt(
        fname,
        dtype=dtypes,
        skip_header=1,
        delimiter='\t'
        )
    return X


def save_tsv(fname, X):
    """TODO: This should be changed so that NaN are not represented"""
    savetxt(
        fname,
        X,
        header='\t'.join(X.dtype.names),
        delimiter='\t',
        fmt=dtype2fmt(X.dtype),
        comments='')
