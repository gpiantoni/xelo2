from numpy import empty
from wonambi import Dataset
from sys import maxsize


def read_events_from_ieeg(run, rec, file):
    """Make sure that rec.offset is in the good direction"""
    d = Dataset(file.path)
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


def find_micromed_in_run(run):
    for rec in run.list_recordings():
        if rec.Manufacturer == 'Micromed':
            for file in rec.list_files():
                if file.format == 'micromed':
                    return rec, file
    return None, None
