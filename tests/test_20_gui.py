from datetime import datetime

from xelo2.database.create import open_database, close_database
from xelo2.api import Subject, Channels
# from xelo2.gui.interface import Interface

from .paths import DB_ARGS


def test_add_items():
    """useful when testing GUI"""
    db = open_database(**DB_ARGS)

    subj = Subject(db, 'marshall')
    sess = subj.list_sessions()[0]
    fake_time = datetime(2000, 3, 1, 10, 0, 0)
    run = sess.add_run('picnam', fake_time)
    recording = run.add_recording('ieeg')

    chan = Channels.add(db)
    chan.name = 'channels type 2'
    data = chan.empty(5)
    data['name'] = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5']
    data['type'] = 'ECOG'
    chan.data = data
    recording.attach_channels(chan)

    close_database(db)


def test_open_interface(qtbot):
    main = Interface(DB_PATH)
    qtbot.addWidget(main)
