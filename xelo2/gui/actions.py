from PyQt5.QtWidgets import (
    QAction,
    )

def create_menubar(main):
    menubar = main.menuBar()
    menubar.clear()

    # FILE
    menubar.addMenu('Database')
    # connect
    # commit
    # revert
    # close

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
