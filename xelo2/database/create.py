from json import load
from logging import getLogger
from pathlib import Path
from re import match

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

    values = {}
    for table_name, v in TABLES.items():
        values.update(parse_table(db, table_name, v))

    add_experimenters(db, TABLES['experimenters'])

    values.pop('experimenters')  # experimenters is not constraint by the trigger system
    add_triggers(values)

    db.close()

    return values


def parse_table(db, table_name, v, issubtable=False):

    foreign_key = []
    constraints = []
    cmd = []
    values = {table_name: {}}

    for col_name, col_info in v.items():

        if col_name == 'subtables':

            for subtable, subtable_info in col_info.items():
                sub_values = parse_table(db, subtable, subtable_info, issubtable=True)
                values.update(sub_values)

        elif col_name == 'id':
            cmd.append('id INTEGER PRIMARY KEY AUTOINCREMENT')

        elif col_name == 'when':
            continue  # TODO

        elif col_name.endswith('_id'):
            if issubtable and not col_name.endswith('_group_id'):  # channel_group_id and electrode_group_id are not unique
                cmd.append(f'{col_name} INTEGER UNIQUE')
            else:
                cmd.append(f'{col_name} INTEGER')

            ref_table = '_'.join(col_name.split('_')[:-1])
            foreign_key.append(f'FOREIGN KEY({col_name}) REFERENCES {ref_table}s(id) ON DELETE CASCADE')

        else:
            cmd.append(f'{col_name} {col_info["type"]}')

            # 'name' should end with "(run_id)" or "(subject_id)" which then points to the "runs" table or the "subjects" table
            matching = match('.*\(([a-z]*)_id\)', col_info['name'])
            if matching:
                ref_table = matching.group(1)
                foreign_key.append(f'FOREIGN KEY({col_name}) REFERENCES {ref_table}s(id) ON DELETE CASCADE')

        if col_info is not None and "values" in col_info:
            values[table_name][col_name] = []
            for v in col_info['values']:
                values[table_name][col_name].append(v)

    if len(v) == 2 and list(v)[0].endswith('_id') and list(v)[1].endswith('_id'):
        constraints.append(f'CONSTRAINT {table_name}_unique UNIQUE ({list(v)[0]}, {list(v)[1]})')

    cmd.extend(foreign_key)
    cmd.extend(constraints)

    sql_cmd = f'CREATE TABLE {table_name} (\n ' + ',\n '.join(cmd) + '\n)'
    lg.debug(sql_cmd)
    query = QSqlQuery(sql_cmd)
    if not query.isActive():
        lg.warning(query.lastError().databaseText())

    return values


def add_triggers(allowed_values):
    sql_cmd = 'CREATE TABLE allowed_values ( table_name TEXT NOT NULL, column_name TEXT NOT NULL, allowed_value TEXT NOT NULL)'
    query = QSqlQuery(sql_cmd)
    if not query.isActive():
        lg.warning(query.lastError().databaseText())

    for table_name, table_info in allowed_values.items():
        for col_name, col_info in table_info.items():
            for v in col_info:
                query = QSqlQuery(f"""\
                    INSERT INTO allowed_values ("table_name", "column_name", "allowed_value")
                    VALUES ("{table_name}", "{col_name}", "{v}")""")

                if not query.isActive():
                    lg.warning(query.lastError().databaseText())

            for statement in ('INSERT', 'UPDATE'):  # mysql cannot handle both in the same trigger statement
                sql_cmd = f"""\
                CREATE TRIGGER validate_{col_name}_before_{statement.lower()}_to_{table_name}
                   BEFORE {statement} ON {table_name}
                BEGIN
                   SELECT
                      CASE
                    WHEN NEW.{col_name} NOT IN  (
                        SELECT allowed_value FROM allowed_values
                        WHERE table_name == '{table_name}'
                        AND column_name == '{col_name}')
                    THEN
                         RAISE (ABORT, 'Invalid {col_name} for {table_name}')
                    END;
                END;"""

                query = QSqlQuery(sql_cmd)
                if not query.isActive():
                    lg.warning(query.lastError().databaseText())


def add_experimenters(db, table_experimenters):

    for experimenter in table_experimenters['name']['values']:
        assert QSqlQuery(db).exec(f"""\
            INSERT INTO experimenters ("name")
            VALUES ("{experimenter}")""")
