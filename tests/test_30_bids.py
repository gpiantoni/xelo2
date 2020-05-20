# from xelo2.bids.root import prepare_subset, create_bids

from .paths import BIDS_DIR


def test_bids():
    subsets = prepare_subset('subjects.id == "1"')
    create_bids(BIDS_DIR, deface=False, subset=subsets)
