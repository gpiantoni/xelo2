from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
DATA_DIR = TEST_DIR / 'data'
EXPORTED_DIR = DATA_DIR / 'exported'
EXPORTED_DIR.mkdir(exist_ok=True, parents=True)

DB_PATH = EXPORTED_DIR / 'sqlite.db'
