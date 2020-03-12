from collections import defaultdict

from .tables import TABLES


def prepare_query_files(level):

    columns = {
        f'{level}s_files': [
            f'{level}_id',
            ],
        'files': [
            'format',
            'path',
            ],
        }
    query_str = f"""\
        SELECT {level}s_files.{level}_id, files.format, files.path FROM {level}s_files
        JOIN files ON files.id == {level}s_files.file_id"""

    return query_str, columns


def prepare_query_experimenters():

    columns = {
        'runs_experimenters': [
            'run_id',
            ],
        'experimenters': [
            'name',
            ],
        }
    query_str = """\
        SELECT runs_experimenters.run_id, experimenters.name FROM runs_experimenters
        JOIN experimenters ON runs_experimenters.experimenter_id == experimenters.id"""

    return query_str, columns


def prepare_query(tables):
    all_tables = _get_all_tables(tables)
    query_str = prepare_query_str(all_tables)

    columns = defaultdict(list)
    for table_name in all_tables:
        for column_name in get_columns(_get_table(table_name)):
            columns[table_name].append(column_name)
    return query_str, columns


def _get_all_tables(tables):
    """return the main tables and their subtables"""
    ALL_TABLES = []
    for table_name in tables:
        ALL_TABLES.append(table_name)
        for subtable in TABLES[table_name].get('subtables', []):
            ALL_TABLES.append(subtable)

    return ALL_TABLES


def _get_table(table_name):
    if table_name in TABLES:
        return TABLES[table_name]
    else:
        return TABLES[table_name.split('_')[0]]['subtables'][table_name]


def prepare_query_str(all_tables):

    q = []
    for table in all_tables:
        if len(q) == 0:
            q.append(f'SELECT * FROM {table}')
            continue
        elif '_' in table:
            main_table = table.split('_')[0][:-1]
        elif table in 'sessions':
            main_table = 'subject'
        elif table == 'runs':
            main_table = 'session'
        elif table == 'recordings':
            main_table = 'run'
        else:
            print('missing table')
        q.append(f'LEFT JOIN {table} ON {main_table}s.id == {table}.{main_table}_id')

    return '\n'.join(q)


def get_columns(T):
    cols = [x for x in T if x not in ('subtables', 'when')]

    # put ids at the end because they are the least informative when sorting tsv
    cols.sort(key=lambda x: x.endswith('id'))
    return cols
