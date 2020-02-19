from numpy import isnan
from scipy.io import loadmat


def import_electrodes(mat_file, n_chan):

    mat_all = loadmat(mat_file)
    varname = [x for x in mat_all if x[:2] != '__'][0]
    mat = mat_all[varname]

    if mat.shape[0] == n_chan:
        return mat

    has_nan = isnan(mat).all(axis=1)
    mat = mat[~has_nan, :3]

    if mat.shape[0] == n_chan:
        return mat

    return None
