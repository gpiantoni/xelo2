def rename_task(task_name):
    """To be consistent with BIDS (no dashes)"""
    if task_name.startswith('bair_'):
        task_name = task_name[5:]

    task_name = task_name.replace('_', '')

    return task_name


def make_bids_name(bids_name):
    return '_'.join([str(x) for x in bids_name.values() if x is not None])
