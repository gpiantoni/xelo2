from PyQt5.QtSql import QSqlQuery
from ..database import TABLES

MAIN_TABLES = ('subjects', 'sessions', 'protocols', 'runs', 'recordings')


def export_database(OUTPUT_TSV):

    all_tables = _get_all_tables()
    query_str = prepare_query(all_tables)
    query = QSqlQuery(query_str)

    with OUTPUT_TSV.open('w+') as f:

        HEADER = []
        for table_name in all_tables:
            for column_name in columns(_get_table(table_name)):
                HEADER.append(f'{table_name}.{column_name}')

        f.write('\t'.join(HEADER) + '\n')

        while query.next():
            values = []
            for table_name in all_tables:
                TABLE_INFO = _get_table(table_name)
                for column_name in columns(TABLE_INFO):
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


def _get_all_tables():
    """return the main tables and their subtables"""
    ALL_TABLES = []
    for table_name in MAIN_TABLES:
        ALL_TABLES.append(table_name)
        for subtable in TABLES[table_name].get('subtables', []):
            ALL_TABLES.append(subtable)

    return ALL_TABLES


def _get_table(table_name):
    if table_name in TABLES:
        return TABLES[table_name]
    else:
        return TABLES[table_name.split('_')[0]]['subtables'][table_name]


def prepare_query(all_tables):

    q = []
    for table in all_tables:
        if len(q) == 0:
            q.append(f'SELECT * FROM {table}')
            continue
        elif '_' in table:
            main_table = table.split('_')[0][:-1]
        elif table in ('sessions', 'protocols'):
            main_table = 'subject'
        elif table == 'runs':
            main_table = 'session'
        elif table == 'recordings':
            main_table = 'run'
        else:
            print('missing table')
        q.append(f'LEFT JOIN {table} ON {main_table}s.id == {table}.{main_table}_id')

    return '\n'.join(q)


def columns(T):
    cols = [x for x in T if not x.endswith('_id') and x not in ('subtables', 'when')]
    return cols
