from numpy import floating, character, issubdtype
from wonambi import Dataset
from wonambi.ioeeg import BlackRock
from pytz import timezone


def localize_blackrock(path_to_file):
    if path_to_file.suffix == '.nev':  # ns3 has more information (f.e. n_samples when there are no triggers)
        path_to_file = path_to_file.with_suffix('.ns3')

    d = Dataset(path_to_file)

    if d.IOClass == BlackRock:
        start_time = d.header['start_time'].astimezone(timezone('Europe/Amsterdam'))
        d.header['start_time'] = start_time.replace(tzinfo=None)

    return d


def dtype2fmt(dtypes):
    fmt = []

    for dtype_name in dtypes.names:
        if issubdtype(dtypes[dtype_name], floating):
            fmt.append('%.3f')
        elif issubdtype(dtypes[dtype_name], character):
            fmt.append('%s')
        else:
            raise TypeError(f'Unknown type {dtypes[dtype_name]}')

    return fmt
