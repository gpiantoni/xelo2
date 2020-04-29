from datetime import datetime
from pathlib import Path
from lxml.etree import parse
from ...api.structure import Run, Subject


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


def add_subject_to_sql(xml_subj):
    sql_subj = Subject(code=xml_subj['SubjectCode'])

    if 'ProtocolSigned':
        protocol_sql = ', '.join(p.metc for p in sql_subj.list_protocols())
        print(f'SQL  has {protocol_sql}\nxelo has {xml_subj["ProtocolSigned"]}')

    COLUMNS_DONE = [
        'SubjectCode',
        'ProtocolSigned',
    ]
    [xml_subj.pop(col, None) for col in COLUMNS_DONE]

    SQLXML_FIELDS = [
        ('DateOfBirth', 'date_of_birth'),
        ]
    for xml_param, sql_param in SQLXML_FIELDS:
        assign_value(sql_subj, sql_param, xml_subj.pop(xml_param, None))

    if xml_subj:
        print(f'You need to add {", ".join(xml_subj)}')


def add_task_to_sql(task, subsets):
    # subj = Subject(id=subsets['subjects'][0])
    # sess = Session(id=subsets['sessions'][0])
    run = Run(id=subsets['runs'][0])

    COLUMNS_DONE = [
        'TaskMetadataLocation',
        'xelo_stem',
        'Age',
        'ExperimentGridDensity',
        'Protocol',  # TODO: I don't know how to handle Protocol
    ]
    [task.pop(col, None) for col in COLUMNS_DONE]

    SQLXML_FIELDS = [
        ('Performance', 'performance'),
        ('Experimenters', 'experimenters'),
        ]
    for xml_param, sql_param in SQLXML_FIELDS:
        assign_value(run, sql_param, task.pop(xml_param, None))

    if task:
        print(f'You need to add {", ".join(task)}')


def assign_value(run, param, xml_value):
    """xml_value = task.pop('Performance', None)
    """
    if param == 'experimenters':
        _assign_list(run, xml_value)

    else:
        if param in ('date_of_birth', ):
            xml_value = datetime.strptime(xml_value, '%Y-%b-%d').date()
        sql_value = getattr(run, param)
        if xml_value is not None:
            if sql_value is None:
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
