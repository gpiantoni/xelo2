from datetime import datetime

from xelo2.database.create import open_database
from xelo2.api.structure import Subject, Channels
from xelo2.gui.interface import Interface

from .paths import DB_PATH


def test_add_items():
    """useful when testing GUI"""
    db = open_database(DB_PATH)
    db.transaction()

    subj = Subject(code='Subjwithieeg')
    sess = subj.list_sessions()[0]
    fake_time = datetime(2000, 3, 1, 10, 0, 0)
    run = sess.add_run('picnam', fake_time)
    recording = run.add_recording('ieeg')

    chan = Channels()
    chan.name = 'channels type 2'
    data = chan.empty(5)
    data['name'] = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5']
    data['type'] = 'ECOG'
    chan.data = data
    recording.attach_channels(chan)

    db.commit()


def test_open_interface(qtbot):
    main = Interface(DB_PATH)
    qtbot.addWidget(main)
