from datetime import timedelta, datetime
from nibabel.parrec import parse_PAR_header

"""
subj = Subject.add('echten')
sess = subj.add_session('MRI')
sess.MagneticFieldStrength = '3T'
"""


def add_parrec_to_sess(sess, par_folder):
    for par_file in par_folder.glob('*.PAR'):
        print(f'Parsing {par_file}')
        hdr, image = parse_PAR_header(par_file.open())

        info = _get_MRI_info(hdr)
        if not info:
            continue

        exam_date = datetime.strptime(hdr['exam_date'], '%Y.%m.%d / %H:%M:%S')
        # There is no time for individual runs, so we estimate an average duration of 4 minutes
        start_time = exam_date + timedelta(seconds=4 * 60 * hdr['acq_nr'])
        end_time = start_time + timedelta(seconds=hdr['scan_duration'])

        run = sess.add_run(info['task_name'], start_time, end_time)

        if info['task_name'] == 'motor':
            run.left_right = info['left_right']
            run.body_part = info['body_part']

        rec = run.add_recording(info['modality'])

        rec.add_file('parrec', par_file)
        rec.PulseSequenceType = hdr['tech']


def _get_MRI_info(hdr):
    info = {}
    protocol = hdr['protocol_name'].lower()

    if 'mansfield' in protocol or 'anat' in protocol or 't1' in protocol:
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

        if 'tongue' in protocol:
            info['body_part'] = 'tongue'
            info['left_right'] = 'both'
        elif 'motorlhand' in protocol:
            info['body_part'] = 'hand'
            info['left_right'] = 'left'
        elif 'motorrhand' in protocol:
            info['body_part'] = 'hand'
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

    elif 'fa27' in protocol:
        pass

    else:
        print(f'could not parse {hdr["protocol_name"]}')

    return info
