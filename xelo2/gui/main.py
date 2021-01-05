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
        '--mysql', default=None,
        help='MYSQL database')
    parser.add_argument(
        '-U', '--username', default=None,
        help='MYSQL username')
    parser.add_argument(
        '-P', '--password', default=None,
        help='MYSQL password')
    args = parser.parse_args()

    if args.mysql is not None:
        w = Interface(args.mysql, args.username, args.password)
    else:
        w = Interface()

    app.exec()


if __name__ == '__main__':
    main()
