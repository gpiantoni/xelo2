from PyQt5.QtSql import QSqlQuery
from ..database import TABLES
from collections import defaultdict


FILE_LEVELS = ('subject', 'session', 'protocol', 'run', 'recording')


def export_database(OUTPUT):

    OUTPUT.mkdir(exist_ok=True)

    TABLE_INFO = {
        'main.tsv': ('subjects', 'sessions', 'runs', 'recordings'),
        'protocols.tsv': ('protocols', ),
        'runs_protocols.tsv': ('runs_protocols', ),
        'events.tsv': ('events', ),
        'channels.tsv': ('channels', ),
        'channel_groups.tsv': ('channel_groups', ),
        'electrodes.tsv': ('electrodes', ),
        'electrode_groups.tsv': ('electrode_groups', ),
        }

    for file_name, list_of_tables in TABLE_INFO.items():
        query_str, columns = prepare_query(list_of_tables)
        _export_main(OUTPUT / file_name, query_str, columns)

    for level in FILE_LEVELS:
        query_str, columns = prepare_query_files(level)
        _export_main(OUTPUT / f'{level}s_files.tsv', query_str, columns)

        query_str, columns = prepare_query_experimenters()
        _export_main(OUTPUT / 'experimenters.tsv', query_str, columns)


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


def _export_main(OUTPUT_TSV, query_str, columns):

    query = QSqlQuery(query_str)

    with OUTPUT_TSV.open('w+') as f:

        HEADER = []
        for table_name, column_names in columns.items():
            for column_name in column_names:
                HEADER.append(f'{table_name}.{column_name}')

        f.write('\t'.join(HEADER) + '\n')

        while query.next():
            values = []
            for table_name, column_names in columns.items():
                TABLE_INFO = _get_table(table_name)
                for column_name in column_names:
                    val = query.value(f'{table_name}.{column_name}')

                    if TABLE_INFO[column_name] is None:  # id
                        values.append(str(val))
                    elif TABLE_INFO[column_name]['type'] == 'FLOAT':
                        if val == '':
                            values.append('')
                        else:
                            values.append(f'{val:.6f}')
                    elif TABLE_INFO[column_name]['type'] == 'INTEGER':
                        if val == '':
                            values.append('')
                        else:
                            values.append(f'{val:d}')
                    elif TABLE_INFO[column_name]['type'].startswith('TEXT'):
                        values.append(val)
                    elif TABLE_INFO[column_name]['type'] in ('DATE', 'DATETIME'):
                        values.append(val)
                    else:
                        print(TABLE_INFO[column_name]['type'])

            f.write('\t'.join(values) + '\n')

    sort_tsv(OUTPUT_TSV)


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


def sort_tsv(tsv_file):
    with tsv_file.open() as f:
        lines = f.readlines()

    with tsv_file.open('w+') as f:
        f.write(lines[0])
        f.write(''.join(sorted(lines[1:])))


def get_columns(T):
    cols = [x for x in T if x not in ('subtables', 'when')]

    # put ids at the end because they are the least informative when sorting tsv
    cols.sort(key=lambda x: x.endswith('id'))
    return cols
