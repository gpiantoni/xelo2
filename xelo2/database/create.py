from json import load
from logging import getLogger
from pathlib import Path

from PyQt5.QtSql import (
    QSqlDatabase,
    QSqlQuery,
    )

lg = getLogger(__name__)
SQL_TABLES = Path(__file__).parent / 'tables.json'

with SQL_TABLES.open() as f:
    TABLES = load(f)


def open_database(db_name, db_type='QSQLITE'):
    """Open the default database using Qt framework

    Parameters
    ----------
    db_name : str
        for SQLITE, path to database to create
    db_type : str
        one of the Qt SQL drivers (QSQLITE, QMYSQL, QPSQL)

    Returns
    -------
    QSqlDatabase
        default database
    """
    db = QSqlDatabase.addDatabase(db_type)
    assert db.isValid()

    db_name = Path(db_name).resolve()
    db.setDatabaseName(str(db_name))
    db.open()

    assert QSqlQuery(db).exec('PRAGMA foreign_keys = ON;')
    assert QSqlQuery(db).exec('PRAGMA encoding="UTF-8";')

    return db


def create_database(db_name, db_type='QSQLITE'):
    """Create a default database using Qt framework

    Parameters
    ----------
    db_name : str
        for SQLITE, path to database to create
    db_type : str
        one of the Qt SQL drivers (QSQLITE, QMYSQL, QPSQL)
    """
    db = QSqlDatabase.addDatabase(db_type)
    assert db.isValid()

    db_name = Path(db_name).resolve()
    if db_name.exists():
        db_name.unlink()
    db.setDatabaseName(str(db_name))
    db.open()

    assert QSqlQuery(db).exec('PRAGMA foreign_keys = ON;')
    assert QSqlQuery(db).exec('PRAGMA encoding="UTF-8";')

    for table_name, v in TABLES.items():
        parse_table(db, table_name, v)

    add_experimenters(db, TABLES['experimenters'])
    db.close()


def parse_table(db, table_name, v, issubtable=False):

    foreign_key = []
    constraints = []
    cmd = []

    for col_name, col_info in v.items():

        if col_name == 'subtables':

            for subtable, subtable_info in col_info.items():
                parse_table(db, subtable, subtable_info, issubtable=True)

        elif col_name == 'id':
            cmd.append('id INTEGER PRIMARY KEY AUTOINCREMENT')

        elif col_name == 'when':
            continue

        elif col_name.endswith('_id'):
            if issubtable:
                cmd.append(f'{col_name} INTEGER UNIQUE')
            else:
                cmd.append(f'{col_name} INTEGER')

            ref_table = col_name.split('_')[0]
            foreign_key.append(f'FOREIGN KEY({col_name}) REFERENCES {ref_table}s(id) ON DELETE CASCADE')

        else:
            cmd.append(f'{col_name} {col_info["type"]}')

        if col_info is not None and "values" in col_info:
            list_txt = '", "'.join(col_info["values"])
            constraints.append(f'CONSTRAINT {col_name}_type CHECK ({col_name} IN ("{list_txt}"))')

    if table_name == 'runs_experimenters':
        constraints.append(f'CONSTRAINT run_experimenter_unique UNIQUE (run_id, experimenter_id)')

    cmd.extend(foreign_key)
    cmd.extend(constraints)

    sql_cmd = f'CREATE TABLE {table_name} (\n ' + ',\n '.join(cmd) + '\n)'
    lg.debug(sql_cmd)
    assert QSqlQuery(db).exec(sql_cmd)


def add_experimenters(db, table_experimenters):

    for experimenter in table_experimenters['name']['values']:
        assert QSqlQuery(db).exec(f"""\
            INSERT INTO experimenters ("name")
            VALUES ("{experimenter}")""")
