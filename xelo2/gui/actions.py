from PyQt5.QtWidgets import (
    QAction,
    )
from PyQt5.QtSql import QSqlQuery

def create_menubar(main):
    menubar = main.menuBar()
    # menubar.clear()

    # FILE
    menu_db = menubar.addMenu('Database')

    action_connect = QAction('Connect', main)
    action_connect.setEnabled(False)
    menu_db.addAction(action_connect)

    action_commit = QAction('Commit', main)
    action_commit.triggered.connect(main.sql_commit)
    menu_db.addAction(action_commit)

    action_revert = QAction('Rollback', main)
    action_revert.triggered.connect(main.sql_rollback)
    menu_db.addAction(action_revert)

    action_close = QAction('Close', main)
    action_close.triggered.connect(main.sql_close)
    menu_db.addAction(action_close)

    # New
    menu_new = menubar.addMenu('Add ...')
    NEW_ITEMS = {
        'subject': main.new_subject,
        'session': main.new_session,
        'protocol': main.new_protocol,
        'run': main.new_run,
        'recording': main.new_recording,
        'file': lambda x: main.new_file(main),
        }

    for name, method in NEW_ITEMS.items():
        action = QAction(f'new {name}', main)
        action.triggered.connect(method)
        menu_new.addAction(action)

    # search
    menu_search = menubar.addMenu('Search')
    action_search = QAction('WHERE ...', main)
    action_search.triggered.connect(main.sql_search)
    menu_search.addAction(action_search)
    action_clear = QAction('clear', main)
    action_clear.triggered.connect(main.sql_search_clear)
    menu_search.addAction(action_clear)


SEARCH_STATEMENT = """\
    SELECT subjects.id, sessions.id, runs.id, recordings.id FROM subjects
    LEFT JOIN sessions ON sessions.subject_id == subjects.id
    LEFT JOIN sessions_mri ON sessions_mri.session_id == sessions.id
    LEFT JOIN runs ON runs.session_id == sessions.id
    LEFT JOIN recordings ON recordings.run_id == runs.id
    WHERE """


class Search():

    def __init__(self, where=None):
        """TODO: where is not sanitized!!!"""

        self.clear()
        if where is None:
            return

        self.previous = where

        query = QSqlQuery(SEARCH_STATEMENT + where)

        while query.next():
            self.subjects.append(query.value(0))
            self.sessions.append(query.value(1))
            self.runs.append(query.value(2))
            self.recordings.append(query.value(3))

    def clear(self):

        self.subjects = []
        self.sessions = []
        self.runs = []
        self.recordings = []

        self.previous = ''
