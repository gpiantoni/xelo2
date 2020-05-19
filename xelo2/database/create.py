from logging import getLogger
from pathlib import Path
from textwrap import dedent

from PyQt5.QtSql import (
    QSqlDatabase,
    QSqlQuery,
    )

from .tables import TABLES
from .queries import prepare_query_with_column_names


lg = getLogger(__name__)
CONNECTION_NAME = 'xelo2_database'


def open_database(db_type, db_name, username=None, password=None):
    """Open the default database using Qt framework

    Parameters
    ----------
    db_type : str
        driver to use (QSQLITE or QMYSQL)
    db_name : str
        path to database (QSQLITE) or database name (QMYSQL)
    username : str
        user name to open database
    password : str
        password to open database

    Returns
    -------
    QSqlDatabase
        default database
    """
    assert db_type in ('QSQLITE', 'QMYSQL')
    db = QSqlDatabase.addDatabase(db_type, CONNECTION_NAME)
    assert db.isValid()

    if db_type == 'QSQLITE':
        db_name = Path(db_name).resolve()
    else:
        db.setHostName('127.0.0.1')
        db.setUserName(username)
        if password is not None:
            db.setPassword(password)

    db.setDatabaseName(str(db_name))
    db.open()

    if db_type == 'QSQLITE':
        assert QSqlQuery(db).exec('PRAGMA foreign_keys = ON;')
        assert QSqlQuery(db).exec('PRAGMA encoding="UTF-8";')

    return db


def create_database(db_type, db_name, username=None, password=None):
    """Create a default database using Qt framework

    Parameters
    ----------
    db_type : str
        driver to use (QSQLITE or QMYSQL)
    db_name : str
        path to database (QSQLITE) or database name (QMYSQL)
    username : str
        user name to open database
    password : str
        password to open database

    Returns
    -------
    QSqlDatabase
        default database
    """
    assert db_type in ('QSQLITE', 'QMYSQL')
    db = QSqlDatabase.addDatabase(db_type, CONNECTION_NAME)
    assert db.isValid()

    if db_type == 'QSQLITE':
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

    if db_type == 'QSQLITE':
        assert QSqlQuery(db).exec('PRAGMA foreign_keys = ON;')
        assert QSqlQuery(db).exec('PRAGMA encoding="UTF-8";')

    db.transaction()

    for table_name, v in TABLES.items():
        parse_table(db, table_name, v)

    add_experimenters(db, TABLES['experimenters'])

    return db
    add_triggers(db, TABLES)

    add_views()

    db.commit()
    db.close()


def parse_table(db, table_name, v):

    foreign_keys = []
    constraints = []
    cmd = []

    for col_name, col_info in v.items():

        if col_name == 'when':
            continue

        elif col_name == 'id':
            if db.driverName() == 'QSQLITE':
                auto = 'AUTOINCREMENT'
            else:
                auto = 'AUTO_INCREMENT'
            cmd.append(f'id INTEGER PRIMARY KEY {auto}')

        elif col_name.endswith('_id') or "foreign_key" in col_info:
            if col_info is not None and 'foreign_key' in col_info:
                foreign_key = col_info['foreign_key']
            else:
                foreign_key = col_name

            if 'when' in v:  # if sub-table, then make sure it's unique
                cmd.append(f'{col_name} INTEGER UNIQUE')
            else:
                cmd.append(f'{col_name} INTEGER')

            ref_table = '_'.join(foreign_key.split('_')[:-1])
            foreign_keys.append(f'FOREIGN KEY ({col_name}) REFERENCES {ref_table}s (id) ON DELETE CASCADE')

        else:
            cmd.append(f'{col_name} {col_info["type"]}')

    if len(v) == 2 and list(v)[0].endswith('_id') and list(v)[1].endswith('_id'):
        constraints.append(f'CONSTRAINT {table_name}_unique UNIQUE ({list(v)[0]}, {list(v)[1]})')

    cmd.extend(foreign_keys)
    cmd.extend(constraints)

    sql_cmd = f'CREATE TABLE {table_name} (\n ' + ',\n '.join(cmd) + '\n)'

    query = QSqlQuery(db)
    if not query.exec(sql_cmd):
        lg.debug(sql_cmd)
        lg.warning(query.lastError().text())


def add_triggers(db, allowed_values):
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
                if db.driverName() == 'QSQLITE':
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
        query = QSqlQuery(db)
        if not query.exec(sql_cmd):
            lg.debug(sql_cmd)
            lg.warning(query.lastError().databaseText())


def add_views():
    query_str = prepare_query_with_column_names(('subjects', 'sessions', 'runs', 'recordings'))
    sql_cmd = 'CREATE VIEW all_recordings AS \n' + query_str
    query = QSqlQuery(sql_cmd)

    if not query.isActive():
        lg.warning(query.lastError().databaseText())
