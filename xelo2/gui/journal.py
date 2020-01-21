from datetime import datetime

class Journal():

    def __init__(self, path_to_db):

        log_dir = path_to_db.parent / 'journal'
        log_dir.mkdir(exist_ok=True)

        now = datetime.now()
        log_file = log_dir / f'{path_to_db.stem}_{now:%Y%m%d_%H%M%S}.log'

        self.f = log_file.open('w+')

    def add(self, cmd):
        now = datetime.now()
        self.f.write(f'{now:%Y-%m-%d %H:%M:%S}\t{cmd}\n')

    def flush(self):
        self.f.flush()

    def close(self):
        """TODO: remove duplicates in journal"""
        self.f.close()
