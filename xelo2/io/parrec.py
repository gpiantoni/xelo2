from datetime import timedelta, datetime
from nibabel.parrec import parse_PAR_header


def add_parrec_to_sess(sess, par_file):
    hdr, image = parse_PAR_header(par_file.open())

    info = _get_MRI_info(hdr)
    if not info:
        return

    exam_date = datetime.strptime(hdr['exam_date'], '%Y.%m.%d / %H:%M:%S')
    # There is no time for individual runs, so we estimate an average duration of 4 minutes
    start_time = exam_date + timedelta(seconds=4 * 60 * hdr['acq_nr'])
    duration = hdr['scan_duration']

    run = sess.add_run(info['task_name'], start_time, duration)

    if info['task_name'] == 'motor':
        run.left_right = info['left_right']
        run.body_part = info['body_part']

    rec = run.add_recording(info['modality'])

    rec.add_file('parrec', par_file)
    rec.PulseSequenceType = hdr['tech']


def _get_MRI_info(hdr):
    info = {}
    protocol = hdr['protocol_name'].lower()

    if 't2s' in protocol:
        info['task_name'] = 't2star_anatomy_scan'
        info['modality'] = 'T2star'

    elif 'mansfield' in protocol or 'anat' in protocol or 't1' in protocol:
        info['task_name'] = 't1_anatomy_scan'
        info['modality'] = 'T1w'

    elif 'flair' in protocol:
        info['task_name'] = 'flair_anatomy_scan'
        info['modality'] = 'FLAIR'

    elif 'dti' in protocol:
        info['task_name'] = 'DTI'
        info['modality'] = 'dwi'

    elif ('circle' in protocol) or ('motor' in protocol):
        info['task_name'] = 'motor'
        info['modality'] = 'bold'
        info['body_part'] = None
        info['left_right'] = None

        if 'tongue' in protocol:
            info['body_part'] = 'tongue'
            info['left_right'] = 'both'
        elif 'motorlhand' in protocol:
            info['body_part'] = 'hand'
            info['left_right'] = 'left'
        elif 'motorrhand' in protocol:
            info['body_part'] = 'hand'
            info['left_right'] = 'right'
        elif 'motorlfeet' in protocol:
            info['body_part'] = 'foot'
            info['left_right'] = 'left'
        elif 'motorrfeet' in protocol:
            info['body_part'] = 'foot'
            info['left_right'] = 'right'
        elif 'senslhand' in protocol:
            info['body_part'] = 'hand'
            info['left_right'] = 'left'
            info['task_name'] = 'somatosensory'
        elif 'sensrhand' in protocol:
            info['body_part'] = 'hand'
            info['left_right'] = 'right'
            info['task_name'] = 'somatosensory'
        else:
            print(f'Unknown bodypart {protocol}')

    elif ('picnam' in protocol):
        info['task_name'] = 'picnam'
        info['modality'] = 'bold'

    elif ('verbgen' in protocol):
        info['task_name'] = 'verb'
        info['modality'] = 'bold'

    elif ('chill' in protocol):
        info['task_name'] = 'chill'
        info['modality'] = 'bold'

    elif ('syllables' in protocol):
        info['task_name'] = 'syllables'
        info['modality'] = 'bold'

    elif ('angio' in protocol):
        info['task_name'] = 'angiography_scan'
        info['modality'] = 'angio'

    elif ('pd' in protocol):
        info['task_name'] = 'pd_anatomy_scan'
        info['modality'] = 'PD'

    elif 'fa27' in protocol:
        pass

    else:
        print(f'could not parse {hdr["protocol_name"]}, so calling it "rest". PLEASE FIX IT')
        info['task_name'] = 'rest'
        info['modality'] = 'bold'

    return info
