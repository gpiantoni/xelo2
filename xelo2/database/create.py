"""Subtables should have a field called "when" and be called "parents_EXTRA"
"""
from logging import getLogger
from pathlib import Path
from textwrap import dedent

from PyQt5.QtSql import (
    QSqlDatabase,
    QSqlQuery,
    )

from .tables import TABLES
from .queries import prepare_query_with_column_names, sql_in


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
        db_name = Path(db_name).expanduser().resolve()
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


def close_database(db):
    db.close()
    QSqlDatabase.removeDatabase(db.connectionName())


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
        db_name = Path(db_name).expanduser().resolve()
        if db_name.exists():
            db_name.unlink()

    else:

        _drop_create_mysql(db_name, username, password)
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
        create_statement_table(db, table_name, v)

    add_experimenters(db, TABLES['experimenters'])

    add_triggers_to_check_values(db, TABLES)
    add_triggers_to_add_id(db, TABLES)
    add_triggers_to_delete_orphan_files(db, TABLES)

    add_views(db)

    db.commit()
    close_database(db)


def create_statement_table(db, table_name, v):
    """
    Prepare and write CREATE statements for each table

    Parameters
    ----------
    db : instance of QSqlDatabase
        default database
    table_name : str
        name of the table
    v : dict
        where each key is a column of the table
    """
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

            if 'when' in v and col_name == list(v)[0]:  # if sub-table, then make sure that the first index is unique (but not the other ones)
                cmd.append(f'{col_name} INTEGER UNIQUE')
            else:
                cmd.append(f'{col_name} INTEGER')

            ref_table = '_'.join(foreign_key.split('_')[:-1])
            foreign_keys.append(f'FOREIGN KEY ({col_name}) REFERENCES {ref_table}s (id) ON DELETE CASCADE')

        else:
            sql_col = f'{col_name} {col_info["type"]}'
            if 'default' in col_info:
                sql_col += f' DEFAULT {col_info["default"]}'
            cmd.append(sql_col)

    if len(v) == 2 and list(v)[0].endswith('_id') and list(v)[1].endswith('_id'):
        constraints.append(f'CONSTRAINT {table_name}_unique UNIQUE ({list(v)[0]}, {list(v)[1]})')

    cmd.extend(foreign_keys)
    cmd.extend(constraints)

    sql_cmd = f'CREATE TABLE {table_name} (\n ' + ',\n '.join(cmd) + '\n)'

    query = QSqlQuery(db)
    if not query.exec(sql_cmd):
        lg.debug(sql_cmd)
        lg.warning(query.lastError().text())


def add_triggers_to_check_values(db, TABLES):
    """Add triggers to check if values are allowed, based on table of allowed_values
    This method is more flexible than using CONSTRAINT because we can easily
    add new values by changing the allowed_values table instead of ALTERing the
    table

    Parameters
    ----------
    db : instance of QSqlDatabase
        default database
    TABLES : dict
        description of tables
    """
    sql_cmd = 'CREATE TABLE allowed_values ( table_name TEXT NOT NULL, column_name TEXT NOT NULL, allowed_value TEXT NOT NULL)'
    query = QSqlQuery(db)
    if not query.exec(sql_cmd):
        lg.debug(sql_cmd)
        lg.warning(query.lastError().text())

    query = QSqlQuery(db)
    query.prepare("""\
        INSERT INTO `allowed_values` (`table_name`, `column_name`, `allowed_value`)
        VALUES (:table_name, :column_name, :allowed_value)""")

    for table_name, table_info in TABLES.items():
        if table_name == 'experimenters':
            continue  # experimenters go into a separate table
        query.bindValue(":table_name", table_name)

        for col_name, col_info in table_info.items():
            query.bindValue(":column_name", col_name)

            if col_info is not None and 'values' in col_info:
                for value in col_info['values']:
                    query.bindValue(":allowed_value", value)
                    if not query.exec():
                        lg.debug(f'{table_name} / {col_name} : "{value}"')
                        lg.warning(query.lastError().text())

                for statement in ('INSERT', 'UPDATE'):  # sql cannot handle both in the same trigger statement
                    if db.driverName() == 'QSQLITE':
                        sql_cmd = dedent(f"""\
                            CREATE TRIGGER validate_{col_name}_before_{statement.lower()}_to_{table_name}
                              BEFORE {statement} ON {table_name}
                            BEGIN
                              SELECT
                                CASE
                                  WHEN NEW.{col_name} NOT IN (
                                    SELECT allowed_value FROM allowed_values
                                    WHERE table_name == '{table_name}'
                                    AND column_name == '{col_name}')
                                THEN
                                  RAISE (ABORT, 'Invalid {col_name} for {table_name}')
                                END;
                            END;""")
                    else:
                        sql_cmd = dedent(f"""\
                            CREATE TRIGGER validate_{col_name}_before_{statement.lower()}_to_{table_name}
                              BEFORE {statement} ON {table_name}
                              FOR EACH ROW
                            BEGIN
                              IF NEW.{col_name} NOT IN (
                                SELECT allowed_value FROM allowed_values
                                WHERE table_name = '{table_name}'
                                AND column_name = '{col_name}')
                              THEN
                                SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column {col_name} is not allowed in table {table_name}';
                              END IF;
                            END;""")

                    trigger_query = QSqlQuery(db)
                    if not trigger_query.exec(sql_cmd):
                        lg.debug(sql_cmd)
                        lg.warning(trigger_query.lastError().text())


def add_triggers_to_add_id(db, TABLES):
    """These triggers add the ID of the main table to the subtables

    Parameters
    ----------
    db : instance of QSqlDatabase
        default database
    TABLES : dict
        description of tables

    TODO
    ----
    I could not think of a nice way to prune the rows when updating the name
    of the session. So, if you have an "MRI" session and you change that
    session to "IEMU", then the sessions_mri will still contain info related to
    that session. Maybe it's not bad to keep this info but it's also not useful
    """
    for table_name, table_info in TABLES.items():
        if 'when' in table_info:
            parent_table = table_name.split('_')[0]
            WHEN = table_info['when']

            if db.driverName() == 'QSQLITE':
                sql_cmd = dedent(f"""\
                    CREATE TRIGGER add_id_to_subtable_{table_name}
                    AFTER INSERT ON {parent_table}
                    WHEN
                      NEW.{WHEN['parameter']} {sql_in(WHEN['value'])}
                    BEGIN
                      INSERT INTO {table_name} ({parent_table[:-1]}_id) VALUES (NEW.id) ;
                    END;""")
            else:
                sql_cmd = dedent(f"""\
                    CREATE TRIGGER add_id_to_subtable_{table_name}
                      AFTER INSERT ON {parent_table}
                      FOR EACH ROW
                    BEGIN
                      IF NEW.{WHEN['parameter']} {sql_in(WHEN['value'])}
                      THEN
                        INSERT INTO {table_name} ({parent_table[:-1]}_id) VALUES (NEW.id) ;
                      END IF;
                    END;""")

            query = QSqlQuery(db)
            if not query.exec(sql_cmd):
                lg.debug(sql_cmd)
                lg.warning(query.lastError().text())

            if db.driverName() == 'QSQLITE':
                sql_cmd = dedent(f"""\
                    CREATE TRIGGER replace_id_to_subtable_{table_name}
                    BEFORE UPDATE ON {parent_table}
                    WHEN
                      NEW.{WHEN['parameter']} <> OLD.{WHEN['parameter']} AND
                      NEW.{WHEN['parameter']} {sql_in(WHEN['value'])}
                    BEGIN
                      INSERT INTO {table_name} ({parent_table[:-1]}_id) VALUES (NEW.id) ;
                    END;""")

            else:
                sql_cmd = dedent(f"""\
                    CREATE TRIGGER replace_id_to_subtable_{table_name}
                      BEFORE UPDATE ON {parent_table}
                      FOR EACH ROW
                    BEGIN
                      IF NEW.{WHEN['parameter']} <> OLD.{WHEN['parameter']} AND
                        NEW.{WHEN['parameter']} {sql_in(WHEN['value'])}
                      THEN
                        INSERT INTO {table_name} ({parent_table[:-1]}_id) VALUES (NEW.id) ;
                      END IF;
                    END;""")

            query = QSqlQuery(db)
            if not query.exec(sql_cmd):
                lg.debug(sql_cmd)
                lg.warning(query.lastError().text())


def add_experimenters(db, table_experimenters):
    """Add table with experimenters. We use a separate table so that we can
    point to them by index
    """
    for experimenter in table_experimenters['name']['values']:
        sql_cmd = dedent(f"""\
            INSERT INTO experimenters (`name`)
            VALUES ('{experimenter}')""")
        query = QSqlQuery(db)
        if not query.exec(sql_cmd):
            lg.debug(sql_cmd)
            lg.warning(query.lastError().text())


def add_views(db):
    """Create a general view with some information that might be useful"""
    query_str = prepare_query_with_column_names(('subjects', 'sessions', 'runs'))
    sql_cmd = 'CREATE VIEW all_recordings AS \n' + query_str
    query = QSqlQuery(db)
    if not query.exec(sql_cmd):
        lg.debug(sql_cmd)
        lg.warning(query.lastError().text())


def add_triggers_to_delete_orphan_files(db, TABLES):
    triggers = trigger_for_orphan_files(TABLES, db.driverName())

    for sql_cmd in triggers:
        query = QSqlQuery(db)
        if not query.exec(sql_cmd):
            lg.debug(sql_cmd)
            lg.warning(query.lastError().text())


def trigger_for_orphan_files(TABLES, db_type):
    table_files = []
    for table in TABLES:
        if table.endswith('_files'):
            table_files.append(table)

    search = []
    for table in table_files:
        search.append(f'NOT EXISTS(SELECT file_id FROM {table} WHERE file_id = OLD.file_id)')
    search_tables = ' AND '.join(search)

    for table in table_files:
        if db_type == 'QSQLITE':
            sql_cmd = dedent(f"""\
                CREATE TRIGGER delete_file_if_no_links_in_{table}
                AFTER DELETE ON {table}
                WHEN
                  {search_tables}
                BEGIN
                  DELETE FROM files WHERE id = OLD.file_id ;
                END""")
        else:
            sql_cmd = dedent(f"""\
                CREATE TRIGGER delete_file_if_no_links_in_{table}
                  AFTER DELETE ON {table}
                  FOR EACH ROW
                BEGIN
                  IF {search_tables}
                  THEN
                    DELETE FROM files WHERE id = OLD.file_id ;
                  END IF ;
                END""")
        yield sql_cmd


def _drop_create_mysql(db_name, username, password):
    db = QSqlDatabase.addDatabase('QMYSQL', 'information_schema')

    db.setHostName('127.0.0.1')
    db.setUserName(username)
    db.setPassword(password)
    db.setDatabaseName('information_schema')
    db.open()

    q = QSqlQuery(db)
    assert q.exec(f'DROP DATABASE IF EXISTS {db_name};')
    assert q.exec(f'CREATE DATABASE {db_name};')
    db.close()
