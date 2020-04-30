from datetime import datetime
from pathlib import Path
from lxml.etree import parse
from ...api.structure import Subject


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
        assert False  # I need to check when this happens

    tasks = []
    for xml_task in timeline.iterchildren():  # it's important it follows the document order
        task = read_xml_task(xml_task, CUTOFF)
        if task is not None:
            tasks.append(task)

    return subj, tasks


def read_xml_task(xml_task, CUTOFF=datetime(1900, 1, 1)):

    task = {}
    for tag in xml_task.iterchildren():  # it's important it follows the document order
        if tag.tag == 'TaskName' and tag.text == 'donotanalyse':
            return None
        if tag.tag == 'TaskMetadataLocation' or CUTOFF < datetime.fromisoformat(tag.get('Date')):
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

def add_subject_to_sql(xml_subj):
    sql_subj = Subject(code=_match_subject(xml_subj['SubjectCode']))

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

    SQLXML_FIELDS = [
        ('ImplantationDate', 'date_of_implantation'),
        ('ExplantationDate', 'date_of_explantation'),
        ]
    sql_sess = get_session(sql_subj)
    for xml_param, sql_param in SQLXML_FIELDS:
        assign_value(sql_sess, sql_param, xml_subj.pop(xml_param, None))

    if xml_subj:
        print(f'You need to add {", ".join(xml_subj)}')

    return sql_subj


def add_task_to_sql(task, run):

    task['start_time'], task['duration'] = get_starttime_duration(task)

    COLUMNS_DONE = [
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
    ]
    [task.pop(col, None) for col in COLUMNS_DONE]

    SQLXML_FIELDS = [
        ('Performance', 'performance'),
        ('Experimenters', 'experimenters'),
        ('TaskDescription', 'task_description'),
        ('BodyPart', 'body_part'),
        ('LeftRight', 'left_right'),
        ('ExecutionImagery', 'execution_imagery'),
        ('start_time', 'start_time'),
        ('duration', 'duration'),
        ]

    for xml_param, sql_param in SQLXML_FIELDS:
        assign_value(run, sql_param, task.pop(xml_param, None))

    if task:
        print(f'You need to add {", ".join(task)}')


def assign_value(run, param, xml_value):
    if xml_value is None or xml_value.strip() == '':
        return

    if param == 'experimenters':
        _assign_list(run, xml_value)

    else:

        if param.startswith('date_of'):
            xml_value = datetime.strptime(xml_value, '%Y-%b-%d').date()
        elif param in ('left_right', 'body_part', 'execution_imagery'):
            xml_value = xml_value.lower()

        sql_value = getattr(run, param)
        if sql_value is None:
            print(f'updating {param} with {xml_value}')
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


def get_session(sql_subj):
    sessions = [sess for sess in sql_subj.list_sessions() if sess.name == 'IEMU']
    if len(sessions) == 1:
        return sessions[0]
    elif len(sessions) == 0:
        return sql_subj.add_session('IEMU')
    else:
        raise ValueError(f'There are {len(sessions)} IEMU sessions for {sql_subj.code}')


def _convert_datetime(ExperimentDate, ExperimentTime):
    ExperimentDate = datetime.strptime(ExperimentDate, '%Y-%b-%d').date()
    ExperimentTime = datetime.strptime(ExperimentTime, '%H:%M').time()
    return datetime.combine(ExperimentDate, ExperimentTime)


def get_starttime_duration(task):
    start_time = _convert_datetime(task['ExperimentDate'], task['ExperimentStartTime'])
    duration = _convert_datetime(task['ExperimentDate'], task['ExperimentStopTime']) - start_time
    return start_time, duration.total_seconds()
