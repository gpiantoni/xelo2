from json import dump
from pathlib import Path
from logging import getLogger
from datetime import date, datetime
from shutil import copy

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtSql import QSqlQuery

from bidso.utils import remove_underscore

from ..api import list_subjects
from .mri import convert_mri
from .ieeg import convert_ieeg
from .events import convert_events
from ..io.export_db import prepare_query
from .utils import rename_task
from .templates import (
    JSON_PARTICIPANTS,
    JSON_SESSIONS,
    )

lg = getLogger(__name__)


def prepare_subset(where, subset=None):

    query_str = prepare_query(('subjects', 'sessions', 'runs', 'recordings'))[0]
    query = QSqlQuery(f"""{query_str} WHERE {where}""")

    if subset is None:
        subset = {'subjects': [], 'sessions': [], 'runs': []}

    while query.next():
        subset['subjects'].append(query.value('subjects.id'))
        subset['sessions'].append(query.value('sessions.id'))
        subset['runs'].append(query.value('runs.id'))

    return subset


def create_bids(data_path, deface=True, subset=None, progress=None):

    if subset is not None:
        subset_subj = set(subset['subjects'])
        subset_sess = set(subset['sessions'])
        subset_run = set(subset['runs'])

    data_path = Path(data_path)
    data_path.mkdir(parents=True, exist_ok=True)

    # the dataset_description.json is used by find_root, in some subscripts
    _make_dataset_description(data_path)

    i = 0
    participants = []
    for subj in list_subjects():
        if subset is not None and subj.id not in subset_subj:
            continue

        # use relative date based on date_of_signature

        protocols = [p.date_of_signature for p in subj.list_protocols()]
        if len(protocols) == 0:
            lg.warning(f'You need to add at least one research protocol for {subj.code}')
            continue

        date_of_signature = min(protocols)
        if date_of_signature is None:
            lg.warning(f'You need to add date_of_signature to the METC of {subj.code}')
            continue

        bids_subj = 'sub-' + subj.code
        subj_path = data_path / bids_subj
        subj_path.mkdir(parents=True, exist_ok=True)

        if subj.date_of_birth is None:
            lg.warning(f'You need to add date_of_birth to {subj.code}')
            age = 'n/a'
        else:
            age = (date_of_signature - subj.date_of_birth).days // 365.2425
            age = f'{age:.0f}'

        participants.append({
            'participant_id': bids_subj,
            'sex': subj.sex,
            'age': age,
            'group': 'patient',
            })

        sess_files = []
        for sess in subj.list_sessions():
            if subset is not None and sess.id not in subset_sess:
                continue

            bids_sess = _make_sess_name(sess)

            sess_path = subj_path / bids_sess
            sess_path.mkdir(parents=True, exist_ok=True)

            sess_files.append({
                'session_id': bids_sess,
                'resection': 'n/a',
                'implantation': 'no',
                'breathing_challenge': 'no',
                })
            if sess.name in ('IEMU', 'OR', 'CT'):
                sess_files[-1]['implantation'] = 'yes'

            run_files = []
            for run in sess.list_runs():
                if subset is not None and run.id not in subset_run:
                    continue

                if len(run.list_recordings()) == 0:
                    lg.warning(f'No recordings for {subj.code}/{run.task_name}')
                    continue

                if progress is not None:
                    progress.setValue(i)
                    i += 1
                    progress.setLabelText(f'Exporting "{subj.code}" / "{sess.name}" / "{run.task_name}"')
                    QGuiApplication.processEvents()

                    if progress.wasCanceled():
                        return

                acquisition = get_bids_acquisition(run)

                if acquisition in ('ieeg', 'func'):
                    task = rename_task(run.task_name)
                    bids_run = f'{bids_subj}_{bids_sess}_task-{task}'
                else:
                    bids_run = f'{bids_subj}_{bids_sess}'
                mod_path = sess_path / acquisition
                mod_path.mkdir(parents=True, exist_ok=True)

                data_name = None
                for rec in run.list_recordings():

                    if rec.modality in ('bold', 'T1w', 'T2w', 'T2star', 'PD', 'FLAIR', 'angio', 'epi'):
                        data_name = convert_mri(run, rec, mod_path, bids_run, deface)

                    elif rec.modality == 'ieeg':
                        if run.duration is None:
                            lg.warning(f'You need to specify duration for {subj.code}/{run.task_name}')
                            continue

                        data_name = convert_ieeg(run, rec, mod_path, bids_run)

                    else:
                        lg.warning(f'Unknown modality {rec.modality} for {rec}')
                        continue

                    if acquisition in ('ieeg', 'func'):
                        base_name = remove_underscore(data_name)
                        convert_events(run, base_name)

                if data_name is None:
                    continue

                run_files.append({
                    'filename': str(data_name.relative_to(data_path)),
                    'acq_time': _set_date_to_1900(date_of_signature, run.start_time).isoformat(),
                    })

            if len(run_files) == 0:
                continue
            tsv_file = sess_path / (bids_subj + '_' + bids_sess + '_scans.tsv')
            _list_scans(tsv_file, run_files)

        tsv_file = subj_path / (bids_subj + '_sessions.tsv')
        _list_scans(tsv_file, sess_files)

        json_sessions = tsv_file.with_suffix('.json')
        copy(JSON_SESSIONS, json_sessions)  # https://github.com/bids-standard/bids-validator/issues/888

    # here the rest
    _make_README(data_path)
    tsv_file = data_path / 'participants.tsv'
    _list_scans(tsv_file, participants)
    json_participants = tsv_file.with_suffix('.json')
    copy(JSON_PARTICIPANTS, json_participants)


def _list_scans(tsv_file, scans):

    with tsv_file.open('w') as f:
        f.write('\t'.join(scans[0].keys()) + '\n')
        for scan in scans:
            for k, v in scan.items():
                if v is None:
                    scan[k] = 'n/a'
            f.write('\t'.join(scan.values()) + '\n')


def _make_dataset_description(data_path):
    """Generate general description of the dataset

    Parameters
    ----------
    data_path : Path
        root BIDS directory
    """

    d = {
        "Name": data_path.name,
        "BIDSVersion": "1.2.1",
        "License": "CCBY",
        "Authors": [
            "Giovanni Piantoni",
            "Nick Ramsey",
            "Natalia Petridou",
            ],
        "Acknowledgements": "",
        "HowToAcknowledge": '',
        "Funding": [
            "NIH R01 MH111417",
            ],
        "ReferencesAndLinks": ["", ],
        "DatasetDOI": ""
        }

    with (data_path / 'dataset_description.json').open('w') as f:
        dump(d, f, ensure_ascii=False, indent=' ')


def get_bids_acquisition(run):
    for recording in run.list_recordings():
        modality = recording.modality
        if modality == 'ieeg':
            return 'ieeg'
        elif modality in ('T1w', 'T2w', 'T2star', 'FLAIR', 'PD', 'angio'):
            return 'anat'
        elif modality in ('bold', 'phase'):
            return 'func'
        elif modality in ('epi', ):
            return 'fmap'
        elif modality in ('ct', ):
            return 'ct'

    raise ValueError(f'I cannot determine BIDS folder for {repr(run)}')


def _make_README(data_path):

    with (data_path / 'README').open('w') as f:
        f.write('Converted with xelo2')


def _set_date_to_1900(base_date, datetime_of_interest):
    return datetime.combine(
        date(1900, 1, 1) + (datetime_of_interest.date() - base_date),
        datetime_of_interest.time())


def _make_sess_name(sess):

    if sess.name == 'MRI':
        sess_name = sess.MagneticFieldStrength.lower()
    else:
        sess_name = sess.name.lower()
    return 'ses-' + sess_name + '01'  # TODO: fix when there are multiple sessions
