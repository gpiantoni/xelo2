from numpy import isnan, transpose
from scipy.io import loadmat

try:
    from h5py import File
except ImportError:
    File = None


def import_electrodes(mat_file, n_chan):

    try:
        mat_all = loadmat(mat_file)
        for varname, mat in mat_all.items():
            if varname.startswith('__'):
                continue
            elec = _find_electrodes(mat, n_chan)
            if elec is not None:
                return elec

    except NotImplementedError:
        if File is None:
            raise ImportError('You need to install h5py to open this file')

        with File(mat_file, 'r') as f:
            for varname in f:
                mat = transpose(f[varname][()])
                elec = _find_electrodes(mat, n_chan)
                if elec is not None:
                    return elec

    return None


def _find_electrodes(mat, n_chan):
    print(f'Number of electrodes in mat file: {mat.shape[0]}')
    if mat.shape[0] == n_chan:
        return mat

    has_nan = isnan(mat).all(axis=1)
    mat = mat[~has_nan, :3]

    print(f'Number of electrodes in mat file without nan: {mat.shape[0]}')
    if mat.shape[0] == n_chan:
        return mat

    return None
