from pathlib import Path
from datetime import datetime, date


from ..api.structure import Subject
from ..database.create import create_database, open_database


def import_database(INPUT, db_file):
    print('it does not import protocols without a corresponding run')
    INPUT = Path(INPUT)
    create_database(db_file)
    db = open_database(db_file)

    _import_main(INPUT)

    db.commit()


def _import_main(INPUT):

    PROTOCOLS = {}
    TSV_MAIN = INPUT / 'main.tsv'
    TSV_PROTOCOLS = INPUT / 'protocols.tsv'

    f_main = TSV_MAIN.open()
    header = f_main.readline()[:-1].split('\t')

    for l in f_main:
        values = l[:-1].split('\t')
        values = [None if v == '' else v for v in values]
        d = {k: v for k, v in zip(header, values)}

        try:
            subj = Subject(code=d['subjects.code'])
        except ValueError:
            subj = Subject.add(d['subjects.code'])

            previous_session_id = None
            previous_session = None
            _setattr(subj, 'subjects', d)

        if d['sessions.id'] is None:
            continue

        if previous_session_id is None or previous_session_id != d['sessions.id']:
            previous_session_id = d['sessions.id']

            session = subj.add_session(d['sessions.name'])
            _setattr(session, 'sessions', d)
            previous_session = session

            previous_run_id = None
            previous_run = None

        else:
            session = previous_session

        if d['runs.id'] is None:
            continue

        if previous_run_id is None or previous_run_id != d['runs.id']:
            previous_run_id = d['runs.id']

            run = session.add_run(d['runs.task_name'])
            _setattr(run, 'runs', d)
            print(d['runs.id'])
            if d['runs.protocol_id'] is not None:
                if d['runs.protocol_id'] in PROTOCOLS:
                    d_protocol = _read_protocol(TSV_PROTOCOLS, d['runs.protocol_id'])
                    PROTOCOLS[d['runs.protocol_id']] = subj.add_protocol(d_protocol['protocols.metc'])
                    _setattr(PROTOCOLS[d['runs.protocol_id']], 'protocols', d_protocol)
                run.attach_protocol(PROTOCOLS[d['runs.protocol_id']])

            previous_run = run

            previous_recording_id = None
            previous_recording = None

        else:
            run = previous_run

        if d['recordings.id'] is None:
            continue

        if previous_recording_id is None or previous_recording_id != d['recordings.id']:
            previous_recording_id = d['recordings.id']

            recording = run.add_recording(d['recordings.modality'])
            _setattr(recording, 'recordings', d)
            previous_recording = recording
        else:
            recording = previous_recording

    f_main.close()


def _setattr(item, name, d):
    for k, v in d.items():
        if k.split('.')[1] == 'id' or v is None:
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
