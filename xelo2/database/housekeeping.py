from pathlib import Path

from ..io.ieeg import read_info_from_ieeg
from ..io.channels import create_channels


def recap(subj, sess, run):
    df = {}

    df['subject'] = subj.code
    df['start_time'] = run.start_time

    metc = subj.list_protocols()
    if len(metc) == 0:
        df['has_metc'] = False
        df['has_metc_date'] = False
    else:
        df['has_metc'] = True
        df['has_metc_date'] = any([x.date_of_signature for x in metc])

    df['has_duration'] = True if run.duration is not None else False
    events = run.events
    df['n_events'] = events.shape[0]
    df['has_events_type'] = 'speech' in events['trial_type']

    recordings = run.list_recordings()
    if len(recordings) == 0:
        df['has_recording'] = False
        df['has_file'] = False
        df['is_micromed'] = False
        df['has_channels'] = False
        df['has_electrodes'] = False
        df['has_t1w_for_elec'] = False

    else:
        df['has_recording'] = True
        if len(recordings) > 1:
            raise ValueError('number of recordings')
        rec = recordings[0]

        files = rec.list_files()
        if len(files) == 1:
            df['has_file'] = True
            df['is_micromed'] = True if files[0].format == 'micromed' else False

        else:
            df['has_file'] = False
            df['is_micromed'] = False

        df['has_channels'] = True if rec.channels is not None else False

        elec = rec.electrodes
        df['has_electrodes'] = True if elec is not None else False
        if elec is not None and elec.intendedFor is not None:
            df['has_t1w_for_elec'] = True
        else:
            df['has_t1w_for_elec'] = False

    return df


def add_recording(run):
    print('adding recording')
    recs = run.list_recordings()
    if len(recs) == 0:
        return run.add_recording('ieeg')
    elif len(recs) == 1:
        return recs[0]
    else:
        raise ValueError('too many recordings')


def add_ieeg_info(run, micromed_path):
    ieeg = read_info_from_ieeg(Path(micromed_path))
    print(ieeg['start_time'])
    print(ieeg['duration'])
    print(f"# events: {ieeg['events'].shape[0]}")
    output = input('ok (y/n)?')
    if output == 'y':
        run.start_time = ieeg['start_time']
        run.duration = ieeg['duration']
        run.events = ieeg['events']


def set_channels(sess, rec):

    if len(sess.list_channels()) == 0:
        chan = None
        for ieeg_path in rec.list_files():
            if ieeg_path.format == 'micromed':
                chan = create_channels(ieeg_path.path)
                break
        if chan is None:
            return
        print('creating channels')
        chan.name = 'clinical'

    elif len(sess.list_channels()) == 1:
        chan = sess.list_channels()[0]

    else:
        raise ValueError('too many channels')

    print('setting channels')
    rec.attach_channels(chan)


def remove_bci2000(rec):
    print('removing bci2000')
    file = rec.list_files()[0]
    if file.format == 'bci2000':
        rec.delete_file(file)


def add_events_type(run):
    print('adding event types')
    EVENTS_TYPE = [
        'task start',
        'music',
        'speech',
        'music',
        'speech',
        'music',
        'speech',
        'music',
        'speech',
        'music',
        'speech',
        'music',
        'speech',
        'music',
        'task end'
        ]
    events = run.events
    assert events.shape[0] == 15
    events['trial_type'] = EVENTS_TYPE
    run.events = events
