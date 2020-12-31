from collections import defaultdict


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
        JOIN files ON files.id = {level}s_files.file_id"""

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
        JOIN experimenters ON runs_experimenters.experimenter_id = experimenters.id"""

    return query_str, columns


def prepare_query(table_names):
    """JOIN all the tables in table_names and create a nice query, with all the
    columns"""
    all_tables = get_tables_and_subtables(table_names)
    query_str = prepare_query_str(all_tables)

    columns = defaultdict(list)
    for table_name in all_tables:
        for column_name in get_columns(table_name):
            columns[table_name].append(column_name)
    return query_str, columns


def prepare_query_with_column_names(table_names):
    query_str, columns = prepare_query(table_names)
    column_names = []
    for k, v in columns.items():
        column_names.extend(f'`{k}`.`{v0}`' for v0 in v if not v0.endswith('id'))  # do not use id
    sql_cmd = query_str.replace('*', ', '.join(column_names))
    return sql_cmd


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
        q.append(f'LEFT JOIN {table} ON {main_table}s.id = {table}.{main_table}_id')

    return '\n'.join(q)


def get_tables_and_subtables(tables_of_interest):
    """Get the tables and their subtables.

    Parameters
    ----------
    tables_of_interest : list of str
        list of table names (only main tables)

    Returns
    -------
    list of str
        all tables in the input, plus all the subtables
    """
    out = list(tables_of_interest)  # copy list

    for t in tables_of_interest:
        for table_name, table_info in TABLES.items():
            if table_name.startswith(t) and 'when' in table_info:
                out.append(table_name)

    return out


def get_columns(T):
    """Get all the columns in one tables. It only excludes "when" because it is
    used by subtables"""
    cols = [x for x in TABLES[T] if x not in ('when', )]

    # put ids at the end because they are the least informative when sorting tsv
    cols.sort(key=lambda x: x.endswith('id'))
    return cols
