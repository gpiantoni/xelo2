from json import dump
from pathlib import Path
from logging import getLogger

from ..model import open_database, list_subjects
from .func import convert_func

lg = getLogger(__name__)


def create_bids(data_path, db, deface=True):

    cur = open_database(db)

    data_path = Path(data_path)
    data_path.mkdir(parents=True, exist_ok=True)

    # the dataset_description.json is used by find_root, in some subscripts
    _make_dataset_description(data_path)

    for subj in list_subjects(cur):
        bids_subj = 'sub-' + subj.code
        subj_path = data_path / bids_subj
        subj_path.mkdir(parents=True, exist_ok=True)

        for sess in subj.list_sessions():
            bids_sess = 'ses-umcu' + sess.name.lower() + '01'  # TODO: fix when there are multiple sessions
            sess_path = subj_path / bids_sess
            sess_path.mkdir(parents=True, exist_ok=True)

            for run in sess.list_runs():
                if run.type in ('ieeg', 'func'):
                    task = _rename_task(run.task_name)
                    bids_run = f'{bids_subj}_{bids_sess}_task-{task}'
                else:
                    bids_run = f'{bids_subj}_{bids_sess}'
                mod_path = sess_path / run.type
                mod_path.mkdir(parents=True, exist_ok=True)

                for rec in run.list_recordings():

                    files = rec.list_files()
                    if len(files) == 0:
                        lg.warning(f'No file for {rec}')
                        continue
                    elif len(files) > 1:
                        lg.warning(f'Too many files for {rec}')  # TODO
                        continue

                    file = files[0]
                    if file.type == 'par':
                        convert_func(run, rec, file, mod_path, bids_run)

                    else:
                        continue

    # here the rest
    _make_README(data_path)


def _rename_task(task_name):
    # TODO: make this a json file

    if task_name.startswith('bair_'):
        task_name = task_name[5:]

    return task_name


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


def _make_README(data_path):

    with (data_path / 'README').open('w') as f:
        f.write('Converted with xelo2')