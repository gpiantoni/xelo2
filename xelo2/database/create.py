from logging import getLogger
from pathlib import Path
from re import match
from textwrap import dedent

from PyQt5.QtSql import (
    QSqlDatabase,
    QSqlQuery,
    )

from .tables import TABLES
from .queries import prepare_query_with_column_names


lg = getLogger(__name__)
DB_TYPE = 'QMYSQL'  # 'QSQLITE', 'QMYSQL'


def open_database(db_name, username=None, password=None):
    """Open the default database using Qt framework

    Parameters
    ----------
    db_name : str
        for SQLITE, path to database to create

    Returns
    -------
    QSqlDatabase
        default database
    """
    db = QSqlDatabase.addDatabase(DB_TYPE)
    assert db.isValid()

    if DB_TYPE == 'SQLITE':
        db_name = Path(db_name).resolve()
    else:
        db.setHostName('127.0.0.1')
        db.setUserName(username)
        if password is not None:
            db.setPassword(password)

    db.setDatabaseName(str(db_name))
    db.open()

    if DB_TYPE == 'SQLITE':
        assert QSqlQuery(db).exec('PRAGMA foreign_keys = ON;')
        assert QSqlQuery(db).exec('PRAGMA encoding="UTF-8";')

    return db


def create_database(db_name, username=None, password=None):
    """Create a default database using Qt framework

    Parameters
    ----------
    db_name : str
        for SQLITE, path to database to create
    """
    db = QSqlDatabase.addDatabase(DB_TYPE)
    assert db.isValid()

    if DB_TYPE == 'SQLITE':
        db_name = Path(db_name).resolve()
        if db_name.exists():
            db_name.unlink()

    else:
        db.setHostName('127.0.0.1')
        db.setUserName(username)
        if password is not None:
            db.setPassword(password)

    db.setDatabaseName(str(db_name))
    db.open()

    if DB_TYPE == 'SQLITE':
        assert QSqlQuery(db).exec('PRAGMA foreign_keys = ON;')
        assert QSqlQuery(db).exec('PRAGMA encoding="UTF-8";')

    db.transaction()

    values = {}
    for table_name, v in TABLES.items():
        values.update(parse_table(db, table_name, v))

    add_experimenters(db, TABLES['experimenters'])

    values.pop('experimenters')  # experimenters is not constraint by the trigger system
    add_triggers(values)

    add_views()

    db.commit()
    db.close()

    return values


def parse_table(db, table_name, v, issubtable=False):

    foreign_key = []
    constraints = []
    cmd = []
    sub_commands = []
    values = {table_name: {}}

    for col_name, col_info in v.items():

        if col_name == 'subtables':

            for subtable, subtable_info in col_info.items():
                sub_values, sub_cmd = parse_table(db, subtable, subtable_info, issubtable=True)
                values.update(sub_values)
                sub_commands.append(sub_cmd)

        elif col_name == 'id':
            auto = 'AUTO_INCREMENT'
            if DB_TYPE == 'SQLITE':
                auto = 'AUTOINCREMENT'
            cmd.append(f'id INTEGER PRIMARY KEY {auto}')

        elif col_name == 'when':
            continue  # TODO

        elif col_name.endswith('_id'):
            if issubtable and not col_name.endswith('_group_id'):  # channel_group_id and electrode_group_id are not unique
                cmd.append(f'{col_name} INTEGER UNIQUE')
            else:
                cmd.append(f'{col_name} INTEGER')

            ref_table = '_'.join(col_name.split('_')[:-1])
            foreign_key.append(f'FOREIGN KEY ({col_name}) REFERENCES {ref_table}s (id) ON DELETE CASCADE')

        else:
            cmd.append(f'{col_name} {col_info["type"]}')

            # 'name' should end with "(run_id)" or "(subject_id)" which then points to the "runs" table or the "subjects" table
            matching = match('.*\(([a-z]*)_id\)', col_info['name'])
            if matching:
                ref_table = matching.group(1)
                foreign_key.append(f'FOREIGN KEY ({col_name}) REFERENCES {ref_table}s (id) ON DELETE CASCADE')

        if col_info is not None and "values" in col_info:
            values[table_name][col_name] = []
            for v in col_info['values']:
                values[table_name][col_name].append(v)

    if len(v) == 2 and list(v)[0].endswith('_id') and list(v)[1].endswith('_id'):
        constraints.append(f'CONSTRAINT {table_name}_unique UNIQUE ({list(v)[0]}, {list(v)[1]})')

    cmd.extend(foreign_key)
    cmd.extend(constraints)

    sql_cmd = f'CREATE TABLE {table_name} (\n ' + ',\n '.join(cmd) + '\n)'

    if not issubtable:
        lg.debug(sql_cmd)
        query = QSqlQuery(sql_cmd)
        if not query.isActive():
            lg.warning(query.lastError().databaseText())

        for sub_cmd in sub_commands:
            lg.debug(sql_cmd)
            query = QSqlQuery(sub_cmd)
            if not query.isActive():
                lg.warning(query.lastError().databaseText())

        return values

    else:
        return values, sql_cmd


def add_triggers(allowed_values):
    sql_cmd = 'CREATE TABLE allowed_values ( table_name TEXT NOT NULL, column_name TEXT NOT NULL, allowed_value TEXT NOT NULL)'
    query = QSqlQuery(sql_cmd)
    if not query.isActive():
        lg.warning(query.lastError().databaseText())

    for table_name, table_info in allowed_values.items():
        for col_name, col_info in table_info.items():
            for v in col_info:
                query = QSqlQuery(f"""\
                    INSERT INTO `allowed_values` (`table_name`, `column_name`, `allowed_value`)
                    VALUES ('{table_name}', '{col_name}', '{v}')""")

                if not query.isActive():
                    lg.warning(query.lastError().databaseText())

            for statement in ('INSERT', 'UPDATE'):  # mysql cannot handle both in the same trigger statement
                if DB_TYPE == 'SQLITE':
                    sql_cmd = f"""\
                    CREATE TRIGGER validate_{col_name}_before_{statement.lower()}_to_{table_name}
                       BEFORE {statement} ON {table_name}
                    BEGIN
                       SELECT
                          CASE
                        WHEN NEW.{col_name} NOT IN  (
                            SELECT allowed_value FROM allowed_values
                            WHERE table_name == `{table_name}`
                            AND column_name == `{col_name}`)
                        THEN
                             RAISE (ABORT, 'Invalid {col_name} for {table_name}')
                        END;
                    END;"""
                else:
                    sql_cmd = f"""\
                        CREATE TRIGGER validate_{col_name}_before_{statement.lower()}_to_{table_name}
                          BEFORE {statement} ON {table_name}
                          FOR EACH ROW
                        BEGIN
                          IF NEW.{col_name} NOT IN  (
                            SELECT allowed_value FROM allowed_values
                            WHERE table_name = '{table_name}'
                            AND column_name = '{col_name}')
                          THEN
                            SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column {col_name} is not allowed in table {table_name}';
                          END IF;
                        END;
                    """

                query = QSqlQuery(sql_cmd)
                if not query.isActive():
                    print(sql_cmd)
                    lg.warning(query.lastError().databaseText())


def add_experimenters(db, table_experimenters):

    for experimenter in table_experimenters['name']['values']:
        sql_cmd = dedent(f"""\
            INSERT INTO experimenters (`name`)
            VALUES ('{experimenter}')""")
        query = QSqlQuery(sql_cmd)
        if not query.isActive():
            lg.warning(query.lastError().databaseText())


def add_views():
    query_str = prepare_query_with_column_names(('subjects', 'sessions', 'runs', 'recordings'))
    sql_cmd = 'CREATE VIEW all_recordings AS \n' + query_str
    query = QSqlQuery(sql_cmd)

    if not query.isActive():
        lg.warning(query.lastError().databaseText())
