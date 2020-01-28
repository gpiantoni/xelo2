from xelo2.database.create import create_database, open_database
from xelo2.api.structure import Subject
from xelo2.gui.interface import Interface

from .paths import DB_PATH


def test_setup_database():
    create_database(DB_PATH)
    open_database(DB_PATH)


def test_open_interface(qtbot):
    main = Interface(DB_PATH)
    qtbot.addWidget(main)

