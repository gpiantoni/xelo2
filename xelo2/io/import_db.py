from pathlib import Path
from datetime import datetime, date

from ..api.structure import Subject
from ..database.create import create_database, open_database


def import_database(INPUT, db_file):
    INPUT = Path(INPUT)
    create_database(db_file)
    db = open_database(db_file)

    IDS = {
        'subjects': {},
        'sessions': {},
        'runs': {},
        'recordings': {},
        'protocols': {},
        }

    IDS = _import_main(
        INPUT / 'main.tsv',
        IDS)
    IDS = _import_protocols(
        INPUT / 'protocols.tsv',
        IDS)
    _import_runs_protocols(
        INPUT / 'runs_protocols.tsv',
        IDS)

    db.commit()


def _read_tsv(TSV_FILE):

    f = TSV_FILE.open()
    header = f.readline()[:-1].split('\t')

    for l in f:
        values = l[:-1].split('\t')
        values = [None if v == '' else v for v in values]
        d = {k: v for k, v in zip(header, values)}
        yield d


def _import_runs_protocols(TSV_FILE, IDS):

    for d in _read_tsv(TSV_FILE):
        run = IDS['runs'][d['runs_protocols.run_id']]
        protocol = IDS['protocols'][d['runs_protocols.protocol_id']]
        run.attach_protocol(protocol)


def _import_protocols(TSV_FILE, IDS):

    f = TSV_FILE.open()
    header = f.readline()[:-1].split('\t')

    for l in f:
        values = l[:-1].split('\t')
        values = [None if v == '' else v for v in values]
        d = {k: v for k, v in zip(header, values)}

        subj = IDS['subjects'][d['protocols.subject_id']]

        protocol = subj.add_protocol(d['protocols.metc'])
        _setattr(protocol, 'protocols', d)
        IDS['protocols'][d['protocols.id']] = protocol

    return IDS


def _import_main(TSV_MAIN, IDS):

    f_main = TSV_MAIN.open()
    header = f_main.readline()[:-1].split('\t')

    for l in f_main:
        values = l[:-1].split('\t')
        values = [None if v == '' else v for v in values]
        d = {k: v for k, v in zip(header, values)}

        if d['subjects.id'] in IDS['subjects']:
            subj = IDS['subjects'][d['subjects.id']]

        else:
            subj = Subject.add(d['subjects.code'])
            IDS['subjects'][d['subjects.id']] = subj
            _setattr(subj, 'subjects', d)

        if d['sessions.id'] is None:
            continue

        elif d['sessions.id'] in IDS['sessions']:
            session = IDS['sessions'][d['sessions.id']]

        else:
            session = subj.add_session(d['sessions.name'])
            IDS['sessions'][d['sessions.id']] = session
            _setattr(session, 'sessions', d)

        if d['runs.id'] is None:
            continue

        elif d['runs.id'] in IDS['runs']:
            run = IDS['runs'][d['runs.id']]

        else:
            run = session.add_run(d['runs.task_name'])
            IDS['runs'][d['runs.id']] = run
            _setattr(run, 'runs', d)

        if d['recordings.id'] is None:
            continue

        elif d['recordings.id'] in IDS['recordings']:
            recording = IDS['recordings'][d['recordings.id']]

        else:
            recording = run.add_recording(d['recordings.modality'])
            IDS['recordings'][d['recordings.id']] = recording
            _setattr(recording, 'recordings', d)

    f_main.close()

    return IDS


def _setattr(item, name, d):
    for k, v in d.items():
        if k.endswith('id') or v is None:
            continue
        if k.startswith(f'{name}'):
            if k.split('.')[1].startswith('date_of_'):  # TODO: it should look TABLES up
                v = date.fromisoformat(v)
            elif k.split('.')[1].endswith('time'):  # TODO: it should look TABLES up
                v = datetime.fromisoformat(v)

            setattr(item, k.split('.')[1], v)


def _read_protocol(tsv_protocol, protocol_id):
    with tsv_protocol.open() as f:
        header = f.readline()[:-1].split('\t')

        for l in f:
            values = l[:-1].split('\t')
            values = [None if v == '' else v for v in values]
            d = {k: v for k, v in zip(header, values)}

            if d['protocols.id'] == protocol_id:
                return d
