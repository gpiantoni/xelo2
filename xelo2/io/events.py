from numpy import empty
from wonambi import Dataset
from wonambi.dataset import UnrecognizedFormat
from sys import maxsize
from logging import getLogger

lg = getLogger(__name__)


def read_events_from_ieeg(run, rec, file):
    """Make sure that rec.offset is in the good direction"""
    try:
        d = Dataset(file.path)
    except UnrecognizedFormat:
        lg.warning(f'cannot parse poorly edited BCI2000 file ({file.path})')
        return None
    except FileNotFoundError:
        lg.warning(f'{file.path} does not exist')

    markers = d.read_markers()

    start_t = (run.start_time - d.header['start_time']).total_seconds() + rec.offset
    if run.duration is not None:
        end_t = start_t + run.duration
    else:
        end_t = maxsize

    markers = [m for m in markers if start_t <= m['start'] <= end_t]
    events = empty(len(markers), dtype=run.events.dtype)
    events['value'] = [m['name'] for m in markers]
    events['onset'] = [m['start'] - start_t for m in markers]
    events['duration'] = 0

    return events


def find_eegfile_in_run(run):
    for rec in run.list_recordings():
        for file in rec.list_files():
            if file.format in ('micromed', 'bci2000', 'blackrock'):
                return rec, file
    return None, None
