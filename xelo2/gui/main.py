from pathlib import Path
from argparse import ArgumentParser

from PyQt5.QtWidgets import QApplication

from .interface import Interface
from ..model.structure import open_database


app = QApplication([])


def main():

    parser = ArgumentParser(prog='open xelo2 database')
    parser.add_argument(
        'sqlite',
        nargs='?',
        help='path to ')
    args = parser.parse_args()

    sqlite = Path(args.sqlite).resolve()
    sql, cur = open_database(sqlite)

    w = Interface(cur)
    app.exec()
    sql.close()


if __name__ == '__main__':

    main()
