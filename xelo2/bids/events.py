from bidso.utils import add_underscore
from numpy import floating, character, issubdtype


def convert_events(run, base_name):
    events_tsv = add_underscore(base_name, '_events.tsv')
    events_tsv.touch()


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
