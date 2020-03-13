from numpy import floating, character, issubdtype
from wonambi.ioeeg import BlackRock
from pytz import timezone


def localize_blackrock(d):
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
