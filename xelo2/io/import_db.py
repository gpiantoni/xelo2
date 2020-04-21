from pathlib import Path
from collections import defaultdict
from datetime import datetime, date
from numpy import dtype, unique, genfromtxt

from ..api.structure import Subject, Channels, Electrodes
from ..database.create import create_database, open_database

from .export_db import FILE_LEVELS, _get_table


def import_database(INPUT, db_file):
    INPUT = Path(INPUT)
    create_database(db_file)
    db = open_database(db_file)
    db.transaction()

    IDS = {
        'subjects': {},
        'sessions': {},
        'runs': {},
        'recordings': {},
        'protocols': {},
        'channels': {},
        'electrodes': {},
        }

    for chan_elec in ('channel', 'electrode'):
        IDS[f'{chan_elec}s'] = _add_channels_electrodes(INPUT, chan_elec)

    IDS = _import_main(
        INPUT / 'main.tsv',
        IDS)
    _import_codes(
        INPUT / 'subject_codes.tsv',
        IDS)
    IDS = _import_protocols(
        INPUT / 'protocols.tsv',
        IDS)

    # linking tables
    _import_runs_protocols(
        INPUT / 'runs_protocols.tsv',
        IDS)

    _add_intendedfor_elec(
        INPUT / 'electrode_groups.tsv',
        IDS)

    # files
    for level in FILE_LEVELS:
        _attach_files(INPUT, level, IDS)

    # events
    _attach_events(INPUT / 'events.tsv', IDS)

    _add_experimenters(INPUT / 'experimenters.tsv', IDS)

    db.commit()


def _add_experimenters(TSV_FILE, IDS):

    EXP = defaultdict(list)
    for l in _read_tsv(TSV_FILE):
        EXP[l['runs_experimenters.run_id']].append(l['experimenters.name'])

    for run_id, experimenters in EXP.items():
        IDS['runs'][run_id].experimenters = experimenters


def _read_tsv(TSV_FILE):

    with TSV_FILE.open() as f:
        header = f.readline()[:-1].split('\t')

        for l in f:
            values = l[:-1].split('\t')
            values = [None if v == '' else v for v in values]
            d = {k: v for k, v in zip(header, values)}
            yield d


def _add_channels_electrodes(INPUT, NAME):
    TSV_GROUP_FILE = INPUT / f'{NAME}_groups.tsv'
    TSV_DATA_FILE = INPUT / f'{NAME}s.tsv'

    IDS = {}

    for d in _read_tsv(TSV_GROUP_FILE):
        if NAME == 'channel':
            item = Channels()
        elif NAME == 'electrode':
            item = Electrodes()

        _setattr(item, f'{NAME}_groups', d)
        IDS[d[f'{NAME}_groups.id']] = item

    DTYPE = _get_dtype(TSV_DATA_FILE)

    DATA = genfromtxt(TSV_DATA_FILE, dtype=DTYPE, skip_header=1, delimiter='\t')
    for item_id in unique(DATA[f'{NAME}_group_id']):
        item = IDS[item_id]
        item.data = DATA[DATA[f'{NAME}_group_id'] == item_id]

    return IDS


def _get_dtype(TSV_FILE):
    with TSV_FILE.open() as f:
        header = f.readline()[:-1].split('\t')

    DTYPE = []
    for h in header:
        table_name, column_name = h.split('.')
        info = _get_table(table_name)[column_name]

        if info is None or info['type'].startswith('TEXT'):
            format_ = '<U4096'
        elif info['type'] == 'FLOAT':
            format_ = '<f8'
        else:
            print(info)

        DTYPE.append((column_name, format_))

    return dtype(DTYPE)


def _attach_events(TSV_FILE, IDS):
    DTYPE = _get_dtype(TSV_FILE)

    EVENTS = genfromtxt(TSV_FILE, dtype=DTYPE, skip_header=1, delimiter='\t')
    for run_id in unique(EVENTS['run_id']):
        run = IDS['runs'][run_id]
        run.events = EVENTS[EVENTS['run_id'] == run_id]


def _attach_files(INPUT, level, IDS):
    TSV_FILE = INPUT / f'{level}s_files.tsv'
    for d in _read_tsv(TSV_FILE):
        item = IDS[f'{level}s'][d[f'{level}s_files.{level}_id']]
        path_ = d[f'files.path']
        format_ = d[f'files.format']
        item.add_file(format_, path_)


def _import_runs_protocols(TSV_FILE, IDS):

    for d in _read_tsv(TSV_FILE):
        run = IDS['runs'][d['runs_protocols.run_id']]
        protocol = IDS['protocols'][d['runs_protocols.protocol_id']]
        run.attach_protocol(protocol)


def _add_intendedfor_elec(TSV_GROUP_FILE, IDS):

    for d in _read_tsv(TSV_GROUP_FILE):
        if d['electrode_groups.IntendedFor'] is None:
            continue
        elec = IDS['electrodes'][d['electrode_groups.id']]
        t1_run = IDS['runs'][d['electrode_groups.IntendedFor']]
        elec.IntendedFor = t1_run.id


def _import_protocols(TSV_FILE, IDS):

    for d in _read_tsv(TSV_FILE):
        subj = IDS['subjects'][d['protocols.subject_id']]

        protocol = subj.add_protocol(d['protocols.metc'])
        _setattr(protocol, 'protocols', d)
        IDS['protocols'][d['protocols.id']] = protocol

    return IDS


def _import_codes(TSV_FILE, IDS):

    for d in _read_tsv(TSV_FILE):
        subj = IDS['subjects'][d['subject_codes.subject_id']]
        subj.add_code(d['subject_codes.code'])


def _import_main(TSV_MAIN, IDS):

    for d in _read_tsv(TSV_MAIN):
        if d['subjects.id'] in IDS['subjects']:
            subj = IDS['subjects'][d['subjects.id']]

        else:
            subj = Subject.add()
            _setattr(subj, 'subjects', d)
            IDS['subjects'][d['subjects.id']] = subj

        if d['sessions.id'] is None:
            continue

        elif d['sessions.id'] in IDS['sessions']:
            session = IDS['sessions'][d['sessions.id']]

        else:
            session = subj.add_session(d['sessions.name'])
            _setattr(session, 'sessions', d)
            IDS['sessions'][d['sessions.id']] = session

        if d['runs.id'] is None:
            continue

        elif d['runs.id'] in IDS['runs']:
            run = IDS['runs'][d['runs.id']]

        else:
            run = session.add_run(d['runs.task_name'])
            _setattr(run, 'runs', d)
            IDS['runs'][d['runs.id']] = run

        if d['recordings.id'] is None:
            continue

        elif d['recordings.id'] in IDS['recordings']:
            recording = IDS['recordings'][d['recordings.id']]

        else:
            recording = run.add_recording(d['recordings.modality'])
            _setattr(recording, 'recordings', d)
            if d['recordings_ieeg.channel_group_id'] is not None:
                recording.attach_channels(IDS['channels'][d['recordings_ieeg.channel_group_id']])
            if d['recordings_ieeg.electrode_group_id'] is not None:
                recording.attach_electrodes(IDS['electrodes'][d['recordings_ieeg.electrode_group_id']])
            IDS['recordings'][d['recordings.id']] = recording

    return IDS


def _setattr(item, name, d):
    for k, v in d.items():

        if k.endswith('id') or v is None:
            continue

        if k == 'electrode_groups.IntendedFor':  # this points to an existing run, so we need to do after the runs have been created
            continue

        if k.startswith(f'{name}'):
            if k.split('.')[1].startswith('date_of_'):  # TODO: it should look TABLES up
                v = date.fromisoformat(v)
            elif k.split('.')[1].endswith('time'):  # TODO: it should look TABLES up
                v = datetime.fromisoformat(v)

            setattr(item, k.split('.')[1], v)
