from pathlib import Path
from logging import getLogger
from PyQt5.QtSql import QSqlQuery

from ..database.queries import prepare_query

lg = getLogger(__name__)


def prepare_subset(db, where, subset=None):

    query_str = prepare_query(('subjects', 'sessions', 'runs', 'recordings'))[0]
    query = QSqlQuery(db)
    query.prepare(f"""{query_str} WHERE {where}""")
    if not query.exec():
        raise SyntaxError(query.lastError().text())

    if subset is None:
        subset = {'subjects': [], 'sessions': [], 'runs': []}

    while query.next():
        subset['subjects'].append(query.value('subjects.id'))
        subset['sessions'].append(query.value('sessions.id'))
        subset['runs'].append(query.value('runs.id'))

    return subset


def set_notnone(d, s, field):
    """Set value from field if it's not None
    """
    if s is not None:

        if isinstance(s, dict):
            value = s.get(field, None)
        else:
            value = getattr(s, field)

        if value is not None:
            d[field] = value


def rename_task(task_name):
    """To be consistent with BIDS (no dashes)"""
    if task_name.startswith('bair_'):
        task_name = task_name[5:]

    task_name = task_name.replace('_', '')

    return task_name


def make_bids_name(bids_name, level=None):
    """
    Parameters
    ----------
    level : str
        'channels', 'electrodes', 'coordsystem', 'ieeg', 'physio'
    """
    appendix = ''
    acceptable_levels = ['sub', 'ses', 'task', 'run', 'acq', 'dir', 'rec']
    if level == 'channels':
        acceptable_levels = ['sub', 'ses', 'task', 'acq', 'run']
        appendix = '_channels.tsv'

    elif level == 'electrodes':
        acceptable_levels = ['sub', 'ses', 'acq', 'space']
        appendix = '_electrodes.tsv'

    elif level == 'coordsystem':
        acceptable_levels = ['sub', 'ses', 'acq', 'space']
        appendix = '_coordsystem.json'

    elif level == 'ieeg':
        acceptable_levels = ['sub', 'ses', 'task', 'acq', 'run']  # acq is not official https://neurostars.org/t/two-amplifiers-for-ieeg-recordings/17492
        appendix = '_ieeg.eeg'

    elif level == 'physio':
        acceptable_levels = ['sub', 'ses', 'task', 'run', 'recording']
        appendix = '_physio.tsv.gz'

    values = []
    for k, v in bids_name.items():
        if k in acceptable_levels and v is not None:
            values.append(str(v))

    return '_'.join(values) + appendix


def find_one_file(rec, formats):
    """formats has to be a list"""
    format_str = 'with formats (' + ', '.join(formats) + ')'
    found = []
    for file in rec.list_files():
        if file.format in formats:
            found.append(file)

    if len(found) == 0:
        lg.warning(f'No file {format_str} for {rec}')
        return None

    elif len(found) > 1:
        lg.warning(f'Too many files {format_str} for {rec}')  # TODO
        return None

    file = found[0]
    if not Path(file.path).exists():
        lg.warning(f'{rec} does not exist {format_str}')
        return None

    return file


def make_taskdescription(run):
    """This is only place I can think of where we can put information about
    performance and acquisition"""
    s = []

    FIELDS = [
        'task_description',
        'performance',
        'acquisition',
        ]

    for f in FIELDS:
        value = getattr(run, f)
        if value is not None:
            s.append(value)

    return '; '.join(s)
