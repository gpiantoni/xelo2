from PyQt5.QtWidgets import (
    QAction,
    )

def create_menubar(main):
    menubar = main.menuBar()
    # menubar.clear()

    # FILE
    menu_db = menubar.addMenu('Database')

    action_connect = QAction('Connect', main)
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
