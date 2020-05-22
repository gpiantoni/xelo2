from PyQt5.QtSql import QSqlQuery
from PyQt5.QtCore import QVariant
import sip

from ..database.queries import (
    prepare_query,
    prepare_query_files,
    prepare_query_experimenters,
    _get_table,
    )


FILE_LEVELS = ('subject', 'session', 'protocol', 'run', 'recording')


def export_database(db, OUTPUT):

    OUTPUT.mkdir(exist_ok=True)

    TABLE_INFO = {
        'main.tsv': ('subjects', 'sessions', 'runs', 'recordings'),
        'subject_codes.tsv': ('subject_codes', ),
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
        _export_main(db, OUTPUT / file_name, query_str, columns)

    for level in FILE_LEVELS:
        query_str, columns = prepare_query_files(level)
        _export_main(db, OUTPUT / f'{level}s_files.tsv', query_str, columns)

        query_str, columns = prepare_query_experimenters()
        _export_main(db, OUTPUT / 'experimenters.tsv', query_str, columns)


def _export_main(db, OUTPUT_TSV, query_str, columns):

    query = QSqlQuery(db)

    if not query.exec(query_str):
        raise SyntaxError(query.lastError().text())

    with OUTPUT_TSV.open('w+') as f:

        HEADER = []
        for table_name, column_names in columns.items():
            for column_name in column_names:
                HEADER.append(f'{table_name}.{column_name}')

        f.write('\t'.join(HEADER) + '\n')

        autoconversion = sip.enableautoconversion(QVariant, False)
        while query.next():
            values = []
            for table_name, column_names in columns.items():
                TABLE_INFO = _get_table(table_name)
                for column_name in column_names:
                    val = query.value(f'{table_name}.{column_name}')

                    if TABLE_INFO[column_name] is None or 'foreign_key' in TABLE_INFO[column_name]:
                        values.append(str(val.value()))
                    elif TABLE_INFO[column_name]['type'] == 'FLOAT':
                        if val.isNull():
                            values.append('')
                        else:
                            values.append(f'{val.value():.6f}')
                    elif TABLE_INFO[column_name]['type'] == 'INTEGER':
                        if val.isNull():
                            values.append('')
                        else:
                            values.append(f'{val.value():d}')
                    elif TABLE_INFO[column_name]['type'].startswith('TEXT'):
                        values.append(val.value())
                    elif TABLE_INFO[column_name]['type'] in ('DATE', 'DATETIME'):
                        values.append(val.value())
                    else:
                        print(TABLE_INFO[column_name]['type'])

            f.write('\t'.join([_str(x) for x in values]) + '\n')
        sip.enableautoconversion(QVariant, autoconversion)


def _str(s):
    if s is None:
        return ''
    else:
        return s
