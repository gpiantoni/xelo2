from xelo2.bids.root import prepare_subset, create_bids

from .paths import BIDS_DIR


def test_bids():
    subsets = prepare_subset('subjects.code == "subject_test" AND run.task_name == "t1_anatomy_scan"')
    create_bids(BIDS_DIR, subsets)
