from pathlib import Path
from datetime import datetime, date


from ..api.structure import Subject
from ..database.create import create_database, open_database


def import_database(INPUT, db_file):
    INPUT = Path(INPUT)
    create_database(db_file)
    db = open_database(db_file)
    _import_main(INPUT / 'main.tsv')

    db.commit()


def _import_main(TSV_MAIN):

    with TSV_MAIN.open() as f:
        header = f.readline()[:-1].split('\t')

        for l in f:
            values = l[:-1].split('\t')
            values = [None if v == '' else v for v in values]
            d = {k: v for k, v in zip(header, values)}

            try:
                subj = Subject(code=d['subjects.code'])
            except ValueError:
                subj = Subject.add(d['subjects.code'])

                previous_session_id = None
                previous_session = None

                for k, v in d.items():
                    if k.split('.')[1] == 'id' or v is None:
                        continue
                    if k.startswith('subjects.'):
                        if k.split('.')[1].startswith('date_of_'):  # TODO: it should look TABLES up
                            v = date.fromisoformat(v)
                        elif k.split('.')[1].endswith('time'):  # TODO: it should look TABLES up
                            v = datetime.fromisoformat(v)

                        setattr(subj, k.split('.')[1], v)

            if d['sessions.id'] is None:
                continue

            if previous_session_id is None or previous_session_id != d['sessions.id']:
                previous_session_id = d['sessions.id']

                session = subj.add_session(d['sessions.name'])
                for k, v in d.items():
                    if k.split('.')[1] == 'id' or v is None:
                        continue
                    if k.startswith('sessions'):
                        if k.split('.')[1].startswith('date_of_'):  # TODO: it should look TABLES up
                            v = date.fromisoformat(v)
                        elif k.split('.')[1].endswith('time'):  # TODO: it should look TABLES up
                            v = datetime.fromisoformat(v)
                        setattr(session, k.split('.')[1], v)
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
                for k, v in d.items():
                    if k.split('.')[1] == 'id' or v is None:
                        continue
                    if k.startswith('runs'):
                        if k.split('.')[1].startswith('date_of_'):  # TODO: it should look TABLES up
                            v = date.fromisoformat(v)
                        elif k.split('.')[1].endswith('time'):  # TODO: it should look TABLES up
                            v = datetime.fromisoformat(v)
                        setattr(run, k.split('.')[1], v)
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
                for k, v in d.items():
                    if k.split('.')[1] == 'id' or v is None:
                        continue
                    if k.startswith('recordings'):
                        if k.split('.')[1].startswith('date_of_'):  # TODO: it should look TABLES up
                            v = date.fromisoformat(v)
                        elif k.split('.')[1].endswith('time'):  # TODO: it should look TABLES up
                            v = datetime.fromisoformat(v)
                        setattr(recording, k.split('.')[1], v)
                previous_recording = recording
            else:
                recording = previous_recording

