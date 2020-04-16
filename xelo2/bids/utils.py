from pathlib import Path
from logging import getLogger

lg = getLogger(__name__)


def rename_task(task_name):
    """To be consistent with BIDS (no dashes)"""
    if task_name.startswith('bair_'):
        task_name = task_name[5:]

    task_name = task_name.replace('_', '')

    return task_name


def make_bids_name(bids_name):
    return '_'.join([str(x) for x in bids_name.values() if x is not None])


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
