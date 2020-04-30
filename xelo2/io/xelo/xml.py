from datetime import datetime
from pathlib import Path
from lxml.etree import parse
from ...api.filetype import parse_filetype


def add_run_from_task(task, sql_subj):
    sql_sess = get_session(sql_subj, _match_session(task['Technique']))
    taskname = _match_taskname(task['TaskName'])
    run = sql_sess.add_run(taskname)

    ExperimentLocation = task.pop('ExperimentLocation', '')
    if _match_session(task.pop('Technique', '')) == 'IEMU' and ExperimentLocation:
        rec = run.add_recording('ieeg')
        format = parse_filetype(ExperimentLocation)
        rec.add_file(format, ExperimentLocation)

    add_task_to_sql(task, run)


def read_xml_subject(p_xml_subj, CUTOFF):
    """
    # TODO: where to put info
    # elec_file = generalinfo.find('CtmrElectrodeFileLocation')  # if elec_file but no electrodes in xelo2
    """

    xml_subj = parse(str(p_xml_subj))
    root = xml_subj.getroot()
    assert len(root) in (1, 2)

    generalinfo = root.find('GeneralInformation')
    subj = {}
    for xml_tag in generalinfo.iterchildren():  # it's important it follows the document order
        if xml_tag.tag == 'SubjectCode' or CUTOFF < datetime.fromisoformat(xml_tag.get('Date')):
            subj[xml_tag.tag] = xml_tag.text

    timeline = root.find('Timeline')
    if timeline is None:
        return subj, []

    tasks = []
    for xml_task in timeline.iterchildren():  # it's important it follows the document order
        task = read_xml_task(xml_task, CUTOFF)
        if task is not None:
            tasks.append(task)

    return subj, tasks


def read_xml_task(xml_task, CUTOFF=datetime(1900, 1, 1)):
    READ_ANYWAY = [
        'TaskName',
        'TaskMetadataLocation',
        'ExperimentDate',
        ]

    task = {}
    for tag in xml_task.iterchildren():  # it's important it follows the document order
        if tag.tag == 'TaskName' and tag.text == 'donotanalyse':
            return None
        if tag.tag in READ_ANYWAY or CUTOFF < datetime.fromisoformat(tag.get('Date', '2999-12-31')):
            task[tag.tag] = tag.text

    return read_xml_task_only(task, CUTOFF)


def read_xml_task_only(task, CUTOFF=datetime(1900, 1, 1)):
    try:
        p_task = Path(task['TaskMetadataLocation'])
    except KeyError:
        return None

    assert p_task.exists()

    task['xelo_stem'] = p_task.stem
    tree = parse(str(p_task)).getroot()
    for tag in tree.getchildren():
        if CUTOFF < datetime.fromisoformat(tag.get('Date')):
            task[tag.tag] = tag.text

    return task


def _match_subject(code):
    if code.startswith('intraop'):
        return 'intraop' + code[-3:]
    else:
        return code


def _match_session(name):
    if name.lower() in ('ecog', 'seeg'):
        return 'IEMU'
    elif name.lower() in ('fmri', 'mri'):
        return 'MRI'

def _match_taskname(taskname):
    if taskname == 'visualattention':
        return 'visual_attention'
    else:
        return taskname


def add_subject_to_sql(xml_subj, sql_subj):

    if xml_subj.get('ProtocolSigned', None) is not None:
        protocol_sql = ', '.join(p.metc for p in sql_subj.list_protocols())
        print(f'SQL  has {protocol_sql}\nxelo has {xml_subj["ProtocolSigned"]}')

    COLUMNS_DONE = [
        'SubjectCode',
        'SubjectType',
        'Hemisphere',
        'ProtocolSigned',
        'SubjectFolderLocation',
        'GridDensity',
        ]
    [xml_subj.pop(col, None) for col in COLUMNS_DONE]

    SQLXML_FIELDS = [
        ('DateOfBirth', 'date_of_birth'),
        ('Sex', 'Sex'),
        ]
    for xml_param, sql_param in SQLXML_FIELDS:
        assign_value(sql_subj, sql_param, xml_subj.pop(xml_param, None))

    for session_name in ('IEMU', 'MRI'):
        if session_name == 'IEMU':
            SQLXML_FIELDS = [
                ('ImplantationDate', 'date_of_implantation'),
                ('ExplantationDate', 'date_of_explantation'),
                ]
        elif session_name == 'MRI':
            SQLXML_FIELDS = [  # I don't knowwhat we have here
                ]

        sql_sess = get_session(sql_subj, session_name)
        if sql_sess is not None:
            for xml_param, sql_param in SQLXML_FIELDS:
                assign_value(sql_sess, sql_param, xml_subj.pop(xml_param, None))
        else:
            for xml_param, sql_param in SQLXML_FIELDS:
                xml_value = xml_subj.pop(xml_param, '')
                if xml_value:
                    print(f'this subject has multiple {session_name}, you need to manually add {xml_param}={xml_value}')

    if xml_subj:
        raise ValueError(f'You need to add {", ".join(xml_subj)}')

    return sql_subj


def add_task_to_sql(task, run):

    task['start_time'], task['duration'] = get_starttime_duration(task)
    task['TaskDescription'] = task.get('TaskDescription', '').strip() + ' ' + task.pop('Task_Instruction', '').strip()
    task['Acquisition'] = task.get('Acquisition', '').strip() + ' ' + task.pop('TaskCodes', '').strip() + ' ' + task.pop('InsertFile', '').strip()
    if task.get('Attachments', '').strip():
        for attach in task['Attachments'].split('\\n'):
            run.add_file('task_log', attach.strip())

    COLUMNS_DONE = [
        'Attachments',
        'SubjectCode',
        'TaskName',  # this should be already in there
        'TaskMetadataLocation',
        'xelo_stem',
        'Age',
        'ExperimentGridDensity',
        'Protocol',  # TODO: I don't know how to handle Protocol
        'BadElectrodes',  # TODO: how to handle this
        'ExperimentDate',
        'ExperimentStartTime',
        'ExperimentStopTime',
        'FieldStrength',  # this should go in session
    ]
    [task.pop(col, None) for col in COLUMNS_DONE]

    SQLXML_FIELDS = [
        ('Performance', 'performance'),
        ('Experimenters', 'experimenters'),
        ('TaskDescription', 'task_description'),
        ('Acquisition', 'acquisition'),
        ('BodyPart', 'body_part'),
        ('LeftRight', 'left_right'),
        ('ExecutionImagery', 'execution_imagery'),
        ('OvertCovert', 'overt_covert'),
        ('start_time', 'start_time'),
        ('duration', 'duration'),
        ]

    for xml_param, sql_param in SQLXML_FIELDS:
        assign_value(run, sql_param, task.pop(xml_param, None))

    # remove empty parameters
    task = {k: v for k, v in task.items() if v.strip()}
    if task:
        raise ValueError(f'You need to add {", ".join(task)}')


def assign_value(run, param, xml_value):
    if xml_value is None or (isinstance(xml_value, str) and xml_value.strip() == ''):
        return

    if param == 'experimenters':
        _assign_list(run, xml_value)

    else:

        if param.startswith('date_of'):
            xml_value = datetime.strptime(xml_value, '%Y-%b-%d').date()
        elif param in ('left_right', 'body_part', 'execution_imagery', 'overt_covert'):
            xml_value = xml_value.lower()
        elif isinstance(xml_value, str):
            xml_value = xml_value.strip()

        sql_value = getattr(run, param)
        if sql_value is None:
            # print(f'updating {param} with {xml_value}')
            setattr(run, param, xml_value)
        elif sql_value != xml_value:
            print(f'SQL  has {sql_value}\nxelo has {xml_value}')


def _assign_list(run, xml_value):
    sql_value = run.experimenters
    if xml_value is not None:
        if len(sql_value) == 0:
            run.experimenters = xml_value.split(', ')
        elif sql_value != xml_value:
            print(f'SQL  has {",".join(sql_value)}\nxelo has {xml_value}')


def get_session(sql_subj, sess_name='IEMU'):
    sessions = [sess for sess in sql_subj.list_sessions() if sess.name == sess_name]
    if len(sessions) == 1:
        return sessions[0]
    elif len(sessions) == 0:
        return sql_subj.add_session(sess_name)
    else:
        print(f'There are {len(sessions)} {sess_name} sessions for {sql_subj.code}')
        return None


def _convert_datetime(ExperimentDate, ExperimentTime):
    ExperimentDate = datetime.strptime(ExperimentDate.strip(), '%Y-%b-%d').date()
    ExperimentTime = datetime.strptime(ExperimentTime.strip(), '%H:%M').time()
    return datetime.combine(ExperimentDate, ExperimentTime)


def get_starttime_duration(task):
    if not task.get('ExperimentStartTime', '').strip():
        return None, None
    start_time = _convert_datetime(task['ExperimentDate'], task['ExperimentStartTime'])

    if not task.get('ExperimentStopTime', '').strip():
        return start_time, None

    duration = _convert_datetime(task['ExperimentDate'], task['ExperimentStopTime']) - start_time

    return start_time, duration.total_seconds()
