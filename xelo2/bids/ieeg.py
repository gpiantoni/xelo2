from logging import getLogger
from datetime import timedelta
from wonambi import Dataset
from json import dump

from bidso.utils import remove_underscore, add_underscore

from .utils import find_next_value, rename_task
from ..io.tsv import save_tsv
from ..io.ieeg import localize_blackrock


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

    d = localize_blackrock(Dataset(file_path))
    data = d.read_data(begtime=start_time, endtime=end_time)

    output_ieeg = dest_path / fr'{stem}_run-(\d)_{rec.modality}.eeg'
    output_ieeg = find_next_value(output_ieeg)
    data.export(output_ieeg, 'brainvision', anonymize=True)

    sidecar = _convert_sidecar(run, rec, d)
    sidecar_file = output_ieeg.with_suffix('.json')
    with sidecar_file.open('w') as f:
        dump(sidecar, f, indent=2)

    base_name = remove_underscore(output_ieeg)
    _convert_chan_elec(rec, base_name)
    return output_ieeg


def _convert_chan_elec(rec, base_name):
    channels = rec.channels
    if channels is not None:
        channels_tsv = add_underscore(base_name, 'channels.tsv')
        save_tsv(channels_tsv, channels.data)
        replace_micro(channels_tsv)

    electrodes = rec.electrodes
    if electrodes is not None:
        electrodes_tsv = add_underscore(base_name, 'electrodes.tsv')
        save_tsv(electrodes_tsv, electrodes.data)


def replace_micro(channels_tsv):
    """delete this when the PR is accepted
    https://github.com/bids-standard/bids-validator/pull/923"""
    with channels_tsv.open() as f:
        x = f.read()

    x = x.replace('μ', 'µ')  # 'GREEK SMALL LETTER MU' -> 'MICRO SIGN'

    with channels_tsv.open('w') as f:
        f.write(x)


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


def _convert_sidecar(run, rec, d):
    D = {
        'InstitutionName': 'University Medical Center Utrecht',
        'InstitutionAddress': 'Heidelberglaan 100, 3584 CX Utrecht, the Netherlands',
        'Manufacturer': rec.Manufacturer,
        'TaskName': rename_task(run.task_name),
        'SamplingFrequency': int(d.header['s_freq']),
        'iEEGReference': str(rec.Reference),
        'PowerLineFrequency': 50,
        'SoftwareFilters': 'n/a',
        }
    channels = rec.channels
    if channels is not None:
        chans = channels.data
        for chan_type in ('ECOG', 'SEEG', 'EEG', 'EOG', 'ECG', 'EMG', 'Misc', 'Trigger'):
            D[f'{chan_type}ChannelCount'] = int(sum(chans['type'] == chan_type))
    D['RecordingDuration'] = int(run.duration)
    D['RecordingType'] = 'continuous'
    D['ElectricalStimulation'] = False

    return D
