from logging import getLogger
from datetime import timedelta
from wonambi import Dataset

from bidso.utils import remove_underscore

from .utils import find_next_value

lg = getLogger(__name__)


def convert_ieeg(run, rec, dest_path, stem):
    start_time = run.start_time + timedelta(seconds=rec.offset)
    end_time = start_time + timedelta(seconds=run.duration)

    file = _select_ieeg(rec)
    if file is None:
        return

    file_path = file.path
    if file_path.suffix == '.nev':
        file_path = file_path.with_suffix('.ns3')

    d = Dataset(file_path)
    data = d.read_data(begtime=start_time, endtime=end_time)

    output_ieeg = dest_path / fr'{stem}_run-(\d)_{rec.modality}.eeg'
    output_ieeg = find_next_value(output_ieeg)
    data.export(output_ieeg, 'brainvision')

    return remove_underscore(output_ieeg)


def _select_ieeg(rec):
    ieeg = []
    for file in rec.list_files():
        if file.format in ('blackrock', 'micromed', 'bci2000'):
            ieeg.append(file)

    if len(ieeg) == 0:
        lg.warning(f'No file for {rec}')
        return None

    elif len(ieeg) > 1:
        lg.warning(f'Too many files for {ieeg}')  # TODO
        return None

    file = ieeg[0]
    if not file.path.exists():
        lg.warning(f'{rec} does not exist')
        return None

    return file
