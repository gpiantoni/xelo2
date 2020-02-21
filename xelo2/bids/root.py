from json import dump
from pathlib import Path
from logging import getLogger

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtSql import QSqlQuery

from ..api import list_subjects
from .mri import convert_mri
from .ieeg import convert_ieeg
from .events import convert_events
from ..io.export_db import prepare_query
from .utils import rename_task

lg = getLogger(__name__)


def prepare_subset(where):

    query_str = prepare_query(('subjects', 'sessions', 'runs', 'recordings'))[0]
    query = QSqlQuery(f"""{query_str} WHERE {where}""")

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
    for subj in list_subjects():
        if subset is not None and subj.id not in subset_subj:
            continue

        bids_subj = 'sub-' + subj.code
        subj_path = data_path / bids_subj
        subj_path.mkdir(parents=True, exist_ok=True)

        for sess in subj.list_sessions():
            if subset is not None and sess.id not in subset_sess:
                continue

            bids_sess = 'ses-' + sess.name.lower() + '01'  # TODO: fix when there are multiple sessions
            sess_path = subj_path / bids_sess
            sess_path.mkdir(parents=True, exist_ok=True)

            for run in sess.list_runs():
                if subset is not None and run.id not in subset_run:
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

                for rec in run.list_recordings():

                    if rec.modality in ('bold', 'T1w', 'T2w', 'T2star', 'PD', 'FLAIR', 'angio', 'epi'):
                        base_name = convert_mri(run, rec, mod_path, bids_run)

                    elif rec.modality == 'ieeg':
                        base_name = convert_ieeg(run, rec, mod_path, bids_run)

                    else:
                        lg.warning(f'Unknown modality {rec.modality} for {rec}')
                        continue

                    if acquisition in ('ieeg', 'func'):
                        convert_events(run, base_name)

    # here the rest
    _make_README(data_path)


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
