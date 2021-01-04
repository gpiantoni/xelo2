from pathlib import Path
from os import environ
from shutil import rmtree
from .utils import create_random_rec


TEST_DIR = Path(__file__).resolve().parent
DATA_DIR = TEST_DIR / 'data'
GENERATED_DIR = DATA_DIR / 'generated'
GENERATED_DIR.mkdir(exist_ok=True, parents=True)

if environ.get('CI', '') == 'true':
    DB_ARGS = {
        'db_name': 'test',
        'username': 'travis',
        'password': ''
        }
else:
    DB_ARGS = {
        'db_name': 'test',
        'username': 'giovanni',
        'password': 'password'
        }

LOG_PATH = GENERATED_DIR / 'log_file.txt'

EXAMPLE_DIR = DATA_DIR / 'example'
EXAMPLE_DIR.mkdir(exist_ok=True)

PARREC_DIR = EXAMPLE_DIR / 'parrec'

T1_PATH = PARREC_DIR / 'T1.PAR'
create_random_rec(T1_PATH)

IEEG_DIR = EXAMPLE_DIR / 'ieeg'
TRC_PATH = IEEG_DIR / 'micromed.TRC'

IO_DIR = GENERATED_DIR / 'io'
IO_DIR.mkdir(exist_ok=True)
TSV_PATH = IO_DIR / 'exported_events.tsv'

BIDS_DIR = GENERATED_DIR / 'bids'
try:
    rmtree(BIDS_DIR)
except FileNotFoundError:
    pass
