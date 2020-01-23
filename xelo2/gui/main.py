from pathlib import Path
from logging import getLogger, StreamHandler
from argparse import ArgumentParser
import sys

from PyQt5.QtWidgets import QApplication

from .interface import Interface

lg = getLogger(__name__)
handler = StreamHandler(stream=sys.stdout)
lg.addHandler(handler)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    lg.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

app = QApplication([])


def main():

    parser = ArgumentParser(prog='open xelo2 database')
    parser.add_argument(
        'sqlite',
        nargs='?',
        help='path to ')
    args = parser.parse_args()

    sqlite = Path(args.sqlite).resolve()

    w = Interface(sqlite)
    app.exec()


if __name__ == '__main__':
    main()
