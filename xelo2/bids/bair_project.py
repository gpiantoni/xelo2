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


def add_umcu_to_sub_ses(bids_dir):

    for tsv_file in bids_dir.glob('**/*.tsv'):
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
        txt.append(hdr[:-1] + 'site\thigh_density_grid\tvisual\tmotor\ttactile')

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
                )

    with tsv_file.open('w') as f:
        f.write('\n'.join(txt))


def _find_task_type(subj_path, task_type):
    for t in TASK_TYPES[task_type]:
        if len(list(subj_path.rglob(f'*/*/*_task-{t}_*'))) > 0:
            return 'yes'

    return 'no'
