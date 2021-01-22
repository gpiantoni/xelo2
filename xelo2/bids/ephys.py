from logging import getLogger
from datetime import timedelta
from json import dump

from .utils import rename_task, make_bids_name, find_one_file, make_taskdescription
from ..io.tsv import save_tsv
from ..io.ephys import localize_blackrock


CHAN_TYPES = {
    'ECOGChannelCount': 'ECOG',
    'SEEGChannelCount': 'SEEG',
    'EEGChannelCount': 'EEG',
    'EOGChannelCount': 'EOG',
    'ECGChannelCount': 'ECG',
    'EMGChannelCount': 'EMG',
    'MiscChannelCount': 'MISC',
    'TriggerChannelCount': 'TRIG',
    }


lg = getLogger(__name__)


def convert_ephys(run, rec, dest_path, name, intendedfor):
    start_time = run.start_time + timedelta(seconds=rec.offset)

    end_time = start_time + timedelta(seconds=run.duration)

    file = find_one_file(rec, ('blackrock', 'micromed', 'bci2000'))
    if file is None:
        return

    d = localize_blackrock(file.path)
    data = d.read_data(begtime=start_time, endtime=end_time)

    # get acq from manufacturer. It might be better to use channels.name but
    # I am not sure
    if rec.Manufacturer is None:
        lg.warning(f'Please specify Manufacturer for {run} / {rec}')
        name['acq'] = 'acq-none'
    else:
        name['acq'] = f'acq-{rec.Manufacturer.lower()}'
    output_ephys = dest_path / make_bids_name(name, rec.modality)
    markers = convert_events_to_wonambi(run.events)
    data.export(output_ephys, 'brainvision', markers=markers, anonymize=True)

    sidecar = _convert_sidecar(run, rec, d)
    sidecar_file = output_ephys.with_suffix('.json')
    with sidecar_file.open('w') as f:
        dump(sidecar, f, indent=2)

    n_chan = len(d.header['chan_name'])

    _convert_chan_elec(rec, dest_path, name, intendedfor, n_chan)
    return output_ephys


def _convert_chan_elec(rec, dest_path, name, intendedfor, n_chan):
    channels = rec.channels
    if channels is not None:
        chan_data = channels.data

        if n_chan != chan_data.shape[0]:
            lg.warning(f'{str(rec)}: actual recording has {n_chan} channels, while the channels.tsv has {chan_data.shape[0]} channels')
        channels_tsv = dest_path / make_bids_name(name, 'channels')
        save_tsv(channels_tsv, chan_data, ['name', 'type', 'units', 'low_cutoff', 'high_cutoff'])
        replace_micro(channels_tsv)

    electrodes = rec.electrodes
    if electrodes is not None:
        electrodes_tsv = dest_path / make_bids_name(name, 'electrodes')
        save_tsv(electrodes_tsv, electrodes.data, ['name', 'x', 'y', 'z', 'size'])
        electrodes_json = dest_path / make_bids_name(name, 'coordsystem')
        save_coordsystem(electrodes_json, electrodes, intendedfor)


def replace_micro(channels_tsv):
    """delete this when the PR is accepted
    https://github.com/bids-standard/bids-validator/pull/923"""
    with channels_tsv.open() as f:
        x = f.read()

    x = x.replace('μ', 'µ')  # 'GREEK SMALL LETTER MU' -> 'MICRO SIGN'

    with channels_tsv.open('w') as f:
        f.write(x)


def _convert_sidecar(run, rec, d):
    D = {
        'InstitutionName': 'University Medical Center Utrecht',
        'InstitutionAddress': 'Heidelberglaan 100, 3584 CX Utrecht, the Netherlands',
        'Manufacturer': rec.Manufacturer,
        'TaskName': rename_task(run.task_name),
        'TaskDescription': make_taskdescription(run),
        'SamplingFrequency': int(d.header['s_freq']),
        'PowerLineFrequency': 50,
        'SoftwareFilters': 'n/a',
        }
    channels = rec.channels
    reference = 'n/a'
    if channels is not None:
        if channels.Reference is not None:
            reference = channels.Reference

        chans = channels.data
        for field, chan_type in CHAN_TYPES.items():
            n_chan = int(sum(chans['type'] == chan_type))
            if n_chan > 0:
                D[field] = n_chan

    if rec.modality == 'ieeg':
        D['iEEGReference'] = reference
    elif rec.modality == 'eeg':
        D['EEGReference'] = reference
    D['RecordingDuration'] = run.duration
    D['RecordingType'] = 'continuous'
    if rec.modality == 'ieeg':
        D['ElectricalStimulation'] = False

    return D


def save_coordsystem(electrodes_json, electrodes, intendedfor):
    D = {
        "iEEGCoordinateSystem": "ACPC",  # T1w should be an option https://github.com/bids-standard/bids-specification/issues/661
        "iEEGCoordinateUnits": "mm",
        "iEEGCoordinateProcessingDescription": "surface_projection",
        "iEEGCoordinateProcessingReference": "PMID: 19836416",
        }

    if electrodes.IntendedFor is not None:
        if electrodes.IntendedFor in intendedfor:
            path_to_t1 = intendedfor[electrodes.IntendedFor]
            # assume we have to go back three folders
            path_to_t1 = path_to_t1.relative_to(path_to_t1.parents[3])
            D['IntendedFor'] = '/' + str(path_to_t1)
        else:
            lg.warning(f'Could not find the intended-for t1w for electrodes {electrodes}')

    with electrodes_json.open('w') as f:
        dump(D, f, indent=2)


def convert_events_to_wonambi(events):
    """This function should be in wonambi, once the bids format is more stable
    in wonambi"""
    mrk = []
    for ev in events:
        mrk.append({
            'name': ev['trial_type'],
            'start': ev['onset'],
            'end': ev['onset'] + ev['duration']
        })
    return mrk
