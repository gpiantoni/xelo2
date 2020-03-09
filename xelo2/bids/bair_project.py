from itertools import chain
from bidso.utils import replace_underscore
from json import dump


TASK_TYPES = {
    'visual': [],
    'motor': [],
    'tactile': [
        'vtsprf',
        'vtstemporalpattern',
        ],
    }


def make_bair_compatible(bids_dir):

    add_umcu_to_sub_ses(bids_dir)
    add_info_to_participants(bids_dir)
    add_electrodes(bids_dir)


def add_umcu_to_sub_ses(bids_dir):

    TEXT_FILES = chain(
        bids_dir.glob('**/*.tsv'),
        bids_dir.glob('**/*.vhdr'),
        bids_dir.glob('**/*.vmrk'),
        )

    for tsv_file in TEXT_FILES:
        with tsv_file.open() as f:
            txt = f.read()
        txt = txt.replace('sub-', 'sub-umcu')
        txt = txt.replace('ses-', 'ses-umcu')
        with tsv_file.open('w') as f:
            f.write(txt)

    for subj_path in bids_dir.glob('sub-*'):
        new_subj_path = subj_path.parent / (subj_path.name.replace('sub-', 'sub-umcu'))
        subj_path.rename(new_subj_path)

        for sess_path in new_subj_path.glob('ses-*'):
            new_sess_path = sess_path.parent / (sess_path.name.replace('ses-', 'ses-umcu'))
            sess_path.rename(new_sess_path)

    for old_file in bids_dir.glob('**/*.*'):
        new_name = old_file.name.replace('sub-', 'sub-umcu').replace('ses-', 'ses-umcu')
        old_file.rename(old_file.parent / new_name)


def add_info_to_participants(bids_path):
    """Add some additional information to participants"""
    tsv_file = bids_path / 'participants.tsv'
    with tsv_file.open() as f:
        txt = []
        hdr = f.readline()
        txt.append(hdr[:-1] + '\tsite\thigh_density_grid\tvisual\tmotor\ttactile\tacq_date_shift')

        for l in f:
            subj = l.split('\t')[0]
            txt.append(
                l[:-1]
                + '\tUMCU'
                + '\tno'
                + '\t'
                + _find_task_type(bids_path / subj, 'visual')
                + '\t'
                + _find_task_type(bids_path / subj, 'motor')
                + '\t'
                + _find_task_type(bids_path / subj, 'tactile')
                + '\t0'
                )

    with tsv_file.open('w') as f:
        f.write('\n'.join(txt))


def add_electrodes(bids_dir):

    for bids_ieeg in bids_dir.glob('**/*_ieeg.eeg'):
        _add_empty_elec(bids_ieeg)
        _add_coordsystem(bids_ieeg)

def _add_empty_elec(bids_ieeg):
    elec_file = replace_underscore(bids_ieeg, 'electrodes.tsv')
    if not elec_file.exists():
        with elec_file.open('w') as f:
            f.write('name\tx\ty\tz\tsize\tmaterial\tmanufacturer\tgroup\themisphere\ttype\timpedance\tdimension')


def _add_coordsystem(bids_ieeg):
    D = {
        "iEEGCoordinateSystem": "other",
        "iEEGCoordinateSystemDescription": "native T1w",
        "iEEGCoordinateUnits": "mm",
        "iEEGCoordinateProcessingDescription": "surface_projection",
        "iEEGCoordinateProcessingReference": "PMID: 19836416"
        }

    anat_dir = bids_ieeg.parents[2] / 'ses-umcu3t01' / 'anat'
    anat_t1w = list(anat_dir.glob('*_run-1_T1w.nii.gz'))
    if len(anat_t1w) != 1:
        print(f'{len(anat_t1w)} T1w images found in {anat_dir}')

    else:
        anat_t1w = anat_t1w[0]
        D['IntendedFor'] = str(anat_t1w.relative_to(anat_t1w.parents[3]))

    coordsys_file = replace_underscore(bids_ieeg, 'coordsystem.json')
    with coordsys_file.open('w') as f:
        dump(D, f, indent=2)


def _find_task_type(subj_path, task_type):
    for t in TASK_TYPES[task_type]:
        if len(list(subj_path.rglob(f'*/*/*_task-{t}_*'))) > 0:
            return 'yes'

    return 'no'
