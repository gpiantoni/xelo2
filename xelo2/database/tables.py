from json import load
from pathlib import Path

from PyQt5.QtSql import QSqlQuery


SQL_TABLES = Path(__file__).parent / 'tables.json'

with SQL_TABLES.open() as f:
    TABLES = load(f)


def lookup_allowed_values(db, table, column):
    """Look up allowed values from the table

    Parameters
    ----------
    db : instance of QSqlDatabase

    table : str
        name of the table
    column : str
        name of the column

    Returns
    -------
    list of str
        list of allowed values (it is empty when all the values are allowed)
    """
    query = QSqlQuery(db)
    query.prepare('SELECT allowed_value FROM allowed_values WHERE `table_name` = :table and `column_name` = :column')
    query.bindValue(':table', table)
    query.bindValue(':column', column)
    if not query.exec():
        raise SyntaxError(query.lastError().text())

    values = []
    while query.next():
        values.append(query.value('allowed_value'))

    return values


def lookup_indexes(info_schema, db, table):
    """Look up which columns are indices

    Parameters
    ----------
    info_schema : instance of QSqlDatabase
        this should be the `information_schema` database
    db : instance of QSqlDatabase
        the database with the actual data
    table : str
        name of the table

    Returns
    -------
    dict
        key is the name of the column. The valu
    """
    if not info_schema.databaseName() == 'information_schema':
        raise ValueError('The first argument should be the `information_schema` database, not the database with the data')

    query = QSqlQuery(info_schema)
    query.prepare("""SELECT `column_name`, `referenced_table_name`, `referenced_column_name` FROM `key_column_usage`
        WHERE `table_schema` = :schema AND `table_name` = :table""")
    query.bindValue(':schema', db.databaseName())
    query.bindValue(':table', table)

    if not query.exec():
        raise SyntaxError(query.lastError().text())

    values = {}
    while query.next():
        k = query.value('column_name')
        t = query.value('referenced_table_name')
        c = query.value('referenced_column_name')
        if t == '':
            values[k] = None
        else:
            values[k] = f'{t} ({c})'

    return values
