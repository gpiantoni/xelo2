from datetime import datetime, date
from pytest import raises
from numpy import empty

from xelo2.api import Subject, list_subjects, Electrodes, Channels
from xelo2.api.filetype import parse_filetype
from xelo2.database.create import open_database

from .paths import TRC_PATH, DB_PATH, T1_PATH


def test_api_subject():
    db = open_database(DB_PATH)
    db.transaction()

    subj = Subject.add('subjecttest')
    assert subj.id == 1
    assert str(subj) == '<subject (#1)>'
    assert repr(subj) == 'Subject(code="subjecttest")'

    with raises(ValueError):
        Subject.add('subjecttest')

    with raises(ValueError):
        Subject('does_not_exist')

    subj_copy = Subject('subjecttest')

    assert subj == subj_copy
    assert len({subj, subj_copy}) == 1
    db.commit()


def test_api_session():
    db = open_database(DB_PATH)

    subj = list_subjects()[0]
    sess = subj.add_session('MRI')

    assert sess.id == 1
    assert str(sess) == '<session MRI (#1)>'
    assert repr(sess) == 'Session(id=1)'
    assert sess.subject == subj

    # set attribute in subtable
    with raises(ValueError):
        sess.MagneticFieldStrength = 'not correct'
    sess.MagneticFieldStrength = '3T'
    assert sess.MagneticFieldStrength == '3T'

    with raises(ValueError):
        subj.add_session('xxx')

    sess = subj.add_session('IEMU')
    fake_date = date(2000, 1, 1)
    sess.date_of_implantation = fake_date
    assert sess.date_of_implantation == fake_date
    assert sess.date_of_explantation is None


def test_api_run():
    db = open_database(DB_PATH)
    subj = list_subjects()[0]
    sess = subj.list_sessions()[0]

    fake_time = datetime(2000, 1, 1, 10, 0, 0)
    run = sess.add_run('motor', fake_time)
    assert str(run) == '<run (#1)>'
    assert repr(run) == 'Run(id=1)'
    assert run.session == sess

    assert run.start_time == fake_time
    assert run.duration is None

    run.duration = 10
    assert run.duration == 10

    with raises(ValueError):
        sess.add_run('xxx')


def test_api_protocol():
    db = open_database(DB_PATH)

    subj = list_subjects()[0]
    protocol_1 = subj.add_protocol('14-622')
    assert protocol_1.id == 1

    protocol_2 = subj.add_protocol('16-816')
    assert len(subj.list_protocols()) == 2

    protocol_1.date_of_signature = date(2000, 1, 2)
    assert len(subj.list_protocols()) == 2

    protocol_2.date_of_signature = date(2000, 1, 1)
    assert len(subj.list_protocols()) == 2

    with raises(ValueError):
        subj.add_protocol('xxx')

    sess = subj.list_sessions()[0]
    run = sess.list_runs()[0]
    run.attach_protocol(protocol_1)

    with raises(ValueError):
        run.attach_protocol(protocol_1)

    assert len(run.list_protocols()) == 1

    run.detach_protocol(protocol_1)
    assert len(run.list_protocols()) == 0

    run = sess.list_runs()[0]
    run.attach_protocol(protocol_1)
    run = sess.add_run('mario')
    run.attach_protocol(protocol_2)


def test_api_recording():
    db = open_database(DB_PATH)

    subj = list_subjects()[0]
    sess = subj.list_sessions()[0]
    run = sess.list_runs()[0]

    recording = run.add_recording('ieeg')
    assert str(recording) == '<recording (#1)>'
    assert repr(recording) == 'Recording(id=1)'
    assert recording.run == run

    with raises(ValueError):
        run.add_recording('xxx')

    assert len(run.list_recordings()) == 1

    recording.delete()
    assert len(run.list_recordings()) == 0


def test_api_experimenters():
    db = open_database(DB_PATH)

    subj = list_subjects()[0]
    sess = subj.list_sessions()[0]
    run = sess.list_runs()[0]
    run.experimenters = ['Mariska', 'Gio', 'xxx']
    assert run.experimenters == ['Gio', 'Mariska']


def test_api_events():
    db = open_database(DB_PATH)

    subj = list_subjects()[0]
    sess = subj.list_sessions()[0]
    run = sess.list_runs()[0]
    events = run.events
    assert events.shape == (0, )

    # create fake events
    events = empty(10, dtype=events.dtype)
    events['onset'] = range(10)
    events['duration'] = 3
    events['trial_type'] = 'test'

    run.events = events
    events = run.events
    assert events.shape == (10, )
    assert events['onset'][-1] == 9
    assert events['duration'][5] == 3
    assert events['trial_type'][5] == 'test'


def test_api_files():
    db = open_database(DB_PATH)

    subj = list_subjects()[0]
    file = subj.add_file(parse_filetype(TRC_PATH), TRC_PATH)

    assert len(subj.list_files()) == 1
    assert file.path == TRC_PATH
    assert file.format == 'micromed'

    subj.delete_file(file)
    assert len(subj.list_files()) == 0

    with raises(ValueError):
        subj.add_file('blackrock', TRC_PATH)


def test_api_sorting():
    db = open_database(DB_PATH)

    subj_2 = Subject.add('secondsubject')
    sess = subj_2.add_session('MRI')
    sess.add_run(
        'DTI',
        start_time=datetime(2000, 1, 1, 1, 1),
        duration=300,
        )
    sess.add_run(
        'DTI',
        start_time=datetime(2000, 1, 2, 1, 1),
        )
    sess.add_run('DTI')
    sess.add_run(
        'DTI',
        start_time=datetime(2000, 1, 2, 1, 1),
        )
    assert len(sess.list_runs()) == 4

    Subject.add('thirdsubject')
    assert len(list_subjects()) == 3


def test_api_electrodes_channels():
    db = open_database(DB_PATH)

    elec = Electrodes()
    assert elec.CoordinateUnits == 'mm'

    array = elec.data
    assert array.shape == (0, )

    array = elec.empty(10)

    array['name'] = [f'chan{x}' for x in range(10)]
    array['x'] = range(10)
    array['material'] = 'platinum'

    # TODO: unique electrode name vs unique group_id
    elec.data = array
    array = elec.data

    assert array.shape == (10, )
    assert array['name'][2] == 'chan2'
    assert array['x'][-1] == 9
    assert array['material'][1] == 'platinum'

    # TODO: unique channel name vs unique group_id
    chan = Channels()
    assert chan.Reference == 'n/a'

    values = chan.empty(1)
    values['name'] = 'chan1'
    values['type'] = 'XXX'
    with raises(ValueError):
        chan.data = values


def test_api_electrodes_channels_attach():
    db = open_database(DB_PATH)

    subj = Subject.add('Subjwithieeg')
    sess = subj.add_session('OR')
    run = sess.add_run('motor')
    recording = run.add_recording('ieeg')

    elec = Electrodes()
    data = elec.empty(5)
    data['name'] = ['a0', 'bb', 'cc', 'dd', 'ee']
    data['x'] = range(5)
    elec.data = data

    recording.attach_electrodes(elec)
    assert recording.electrodes.id == elec.id

    recording.detach_electrodes()
    assert recording.electrodes is None

    chan = Channels()
    chan_name = 'channels type 1'
    chan.name = chan_name
    assert chan.name == chan_name
    data = chan.empty(5)
    data['name'] = ['a0', 'bb', 'cc', 'dd', 'ee']
    data['type'] = 'SEEG'
    chan.data = data

    recording.attach_channels(chan)
    assert recording.channels.id == chan.id

    recording.detach_channels()
    assert recording.channels is None

    # add MR to test IntendedFor
    sess = subj.add_session('MRI')
    run = sess.add_run('t1_anatomy_scan')
    recording = run.add_recording('T1w')
    recording.add_file('parrec', T1_PATH)
    elec.IntendedFor = run.id

    # so that it can be tested by export / import
    recording.attach_channels(chan)
    recording.attach_electrodes(elec)

    db.commit()
