TASK_TYPES = {
    'visual': [],
    'motor': [],
    'tactile': [
        'vtsprf',
        'vtstemporalpattern',
        ],
    }


def add_info_to_participants(bids_path):
    """Add some additional information to participants"""
    tsv_file = bids_path / 'participants.tsv'
    with tsv_file.open() as f:
        txt = []
        hdr = f.readline()
        txt.append(hdr[:-1] + '\thigh_density_grid\tvisual\tmotor\ttactile\tacq_date_shift')

        for l in f:
            subj = l.split('\t')[0]
            txt.append(
                l[:-1]
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


def _find_task_type(subj_path, task_type):
    for t in TASK_TYPES[task_type]:
        if len(list(subj_path.rglob(f'*/*/*_task-{t}_*'))) > 0:
            return 'yes'

    return 'no'
