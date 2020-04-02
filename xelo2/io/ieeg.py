from wonambi.ioeeg import BlackRock
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

    d = localize_blackrock(path_to_file)
    mrk = d.read_markers()

    ev = empty(len(mrk), dtype=DTYPES)
    ev['onset'] = [x['start'] for x in mrk]
    ev['duration'] = [x['end'] - x['start'] for x in mrk]
    ev['value'] = [x['name'] for x in mrk]

    if d.IOClass == BlackRock:
        manufacturer = 'BlackRock'
    else:
        manufacturer = 'Micromed'

    info = {
        'start_time': d.header['start_time'],
        'duration': d.header['n_samples'] / d.header['s_freq'],
        'events': ev,
        'manufacturer': manufacturer,
        }
    return info
