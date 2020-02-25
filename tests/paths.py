from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
DATA_DIR = TEST_DIR / 'data'
GENERATED_DIR = DATA_DIR / 'generated'
GENERATED_DIR.mkdir(exist_ok=True, parents=True)

DB_PATH = GENERATED_DIR / 'sqlite.db'
LOG_PATH = GENERATED_DIR / 'log_file.txt'
TRC_PATH = DATA_DIR / 'empty.TRC'

EXPORTED_DIR = GENERATED_DIR / 'export'
EXPORTED_DIR.mkdir(exist_ok=True)

EXPORT_0 = EXPORTED_DIR / 'export_0'
EXPORT_DB = EXPORTED_DIR / 'imported.db'
EXPORT_1 = EXPORTED_DIR / 'export_1'

IO_DIR = GENERATED_DIR / 'io'
IO_DIR.mkdir(exist_ok=True)
TSV_PATH = IO_DIR / 'exported_events.tsv'
