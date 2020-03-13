from wonambi import Dataset

from numpy import empty

from .utils import localize_blackrock
from .events import read_events_from_ieeg
from ..api.structure import _get_dtypes
from ..database import TABLES
from ..api.filetype import parse_filetype


DTYPES = _get_dtypes(TABLES['events'])


def add_ieeg_to_sess(sess, ieeg_file):
    """default task is REST, but TODO decode task from triggers"""

    info = read_info_from_ieeg(ieeg_file)

    # default task is REST
    run = sess.add_run('rest', info['start_time'], info['duration'])
    rec = run.add_recording('ieeg')
    rec.duration = info['duration']
    rec.Manufacturer = info['manufacturer']
    filetype = parse_filetype(ieeg_file)
    file = rec.add_file(filetype, ieeg_file)

    events = read_events_from_ieeg(run, rec, file)
    if len(events) > 0:
        run.events = events

    return run


def read_info_from_ieeg(path_to_file):

    if path_to_file.suffix == '.nev':  # ns3 has more information (f.e. n_samples when there are no triggers)
        path_to_file = path_to_file.with_suffix('.ns3')

    d = localize_blackrock(Dataset(path_to_file))
    mrk = d.read_markers()

    ev = empty(len(mrk), dtype=DTYPES)
    ev['onset'] = [x['start'] for x in mrk]
    ev['duration'] = [x['end'] - x['start'] for x in mrk]
    ev['value'] = [x['name'] for x in mrk]

    if path_to_file.suffix[:3] == '.ns':
        manufacturer = 'BlackRock'
    elif path_to_file.suffix.lower() in ('.trc', '.dat'):
        manufacturer = 'Micromed'

    info = {
        'start_time': d.header['start_time'],
        'duration': d.header['n_samples'] / d.header['s_freq'],
        'events': ev,
        'manufacturer': manufacturer,
        }
    return info
