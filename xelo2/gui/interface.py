from logging import getLogger
from pathlib import Path
from datetime import date, datetime
from functools import partial

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDockWidget,
    QGroupBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QPushButton,
    QDoubleSpinBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    )
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QDesktopServices,
    QGuiApplication,
    QPalette,
    )
from PyQt5.QtCore import (
    Qt,
    pyqtSlot,
    QDate,
    QDateTime,
    QSettings,
    QUrl,
    )
from PyQt5.QtSql import QSqlQuery

from ..api import list_subjects, Subject, Session, Run
from ..database.create import TABLES, open_database
from ..bids.root import create_bids

from .utils import LEVELS
from .actions import create_menubar, Search
from .modal import NewFile, Popup_Experimenters
from .journal import Journal


settings = QSettings("xelo2", "xelo2")
lg = getLogger(__name__)


class Interface(QMainWindow):

    def __init__(self, sqlite_file):
        self.sqlite_file = sqlite_file
        self.journal = Journal(sqlite_file)

        super().__init__()
        self.setWindowTitle(sqlite_file.stem)

        lists = {}
        groups = {}
        for k in LEVELS:
            groups[k] = QGroupBox(k.capitalize())
            lists[k] = QListWidget()
            lists[k].currentItemChanged.connect(self.proc_all)
            # right click
            lists[k].setContextMenuPolicy(Qt.CustomContextMenu)
            lists[k].customContextMenuRequested.connect(partial(self.rightclick_list, level=k))

            layout = QVBoxLayout()
            layout.addWidget(lists[k])
            if k == 'runs':
                b = QPushButton('Add to export list')
                b.clicked.connect(self.exporting)
                layout.addWidget(b)
            groups[k].setLayout(layout)

        # PARAMETERS: Widget
        t_params = QTableWidget()
        t_params.horizontalHeader().setStretchLastSection(True)
        t_params.setSelectionBehavior(QAbstractItemView.SelectRows)
        t_params.setColumnCount(3)
        t_params.setHorizontalHeaderLabels(['Level', 'Parameter', 'Value'])
        t_params.verticalHeader().setVisible(False)

        # FILES: Widget
        t_files = QTableWidget()
        t_files.horizontalHeader().setStretchLastSection(True)
        t_files.setSelectionBehavior(QAbstractItemView.SelectRows)
        t_files.setColumnCount(3)
        t_files.setHorizontalHeaderLabels(['Level', 'Format', 'File'])
        t_files.verticalHeader().setVisible(False)
        # right click
        t_files.setContextMenuPolicy(Qt.CustomContextMenu)
        t_files.customContextMenuRequested.connect(self.rightclick_files)

        # EXPORT: Widget
        w_export = QWidget()
        col_export = QVBoxLayout()

        t_export = QTableWidget()
        t_export.horizontalHeader().setStretchLastSection(True)
        t_export.setSelectionBehavior(QAbstractItemView.SelectRows)
        t_export.setColumnCount(4)
        t_export.setHorizontalHeaderLabels(['Subject', 'Session', 'Run', 'Start Time'])
        t_export.verticalHeader().setVisible(False)

        p_clearexport = QPushButton('Clear list')
        p_clearexport.clicked.connect(self.clear_export)

        p_doexport = QPushButton('Export ...')
        p_doexport.clicked.connect(self.do_export)

        col_export.addWidget(t_export)
        col_export.addWidget(p_clearexport)
        col_export.addWidget(p_doexport)
        w_export.setLayout(col_export)

        # session and protocol in the same column
        col_sessmetc = QVBoxLayout()
        col_sessmetc.addWidget(groups['sessions'])
        col_sessmetc.addWidget(groups['protocols'])

        # TOP PANELS
        layout_top = QHBoxLayout()
        layout_top.addWidget(groups['subjects'])
        layout_top.addLayout(col_sessmetc)
        layout_top.addWidget(groups['runs'])
        layout_top.addWidget(groups['recordings'])

        # FULL LAYOUT
        # central widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(layout_top)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        # parameters
        dockwidget = QDockWidget('Parameters', self)
        dockwidget.setWidget(t_params)
        dockwidget.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        dockwidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        dockwidget.setObjectName('dock_parameters')  # savestate
        self.addDockWidget(Qt.RightDockWidgetArea, dockwidget)

        # files
        dockwidget = QDockWidget('Files', self)
        dockwidget.setWidget(t_files)
        dockwidget.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        dockwidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        dockwidget.setObjectName('dock_files')  # savestate
        self.addDockWidget(Qt.BottomDockWidgetArea, dockwidget)

        # export
        dockwidget = QDockWidget('Export', self)
        dockwidget.setWidget(w_export)
        dockwidget.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        dockwidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        dockwidget.setObjectName('dock_export')  # savestate
        self.addDockWidget(Qt.RightDockWidgetArea, dockwidget)

        # restore geometry
        window_geometry = settings.value('window/geometry')
        if window_geometry is not None:
            self.restoreGeometry(window_geometry)
        window_state = settings.value('window/state')
        if window_state is not None:
            self.restoreState(window_state)

        # SAVE THESE ITEMS
        self.groups = groups
        self.lists = lists
        self.t_params = t_params
        self.t_files = t_files
        self.t_export = t_export
        self.exports = []

        create_menubar(self)
        self.search = Search()

        self.sql_access()
        self.show()

    def sql_access(self):
        """This is where you access the database
        """
        self.sql = open_database(self.sqlite_file)
        self.sql.transaction()
        self.list_subjects()

    def sql_commit(self):
        self.sql.commit()
        self.journal.add('sql.commit()')
        self.journal.flush()

    def sql_rollback(self):
        self.sql.rollback()
        self.journal.add('sql.rollback()')

    def sql_close(self):
        self.sql.close()
        self.journal.add('sql.close()')

    def list_subjects(self):
        for l in self.lists.values():
            l.clear()

        for subj in list_subjects():
            item = QListWidgetItem(subj.code)
            if subj.id in self.search.subjects:
                highlight(item)
            item.setData(Qt.UserRole, subj)
            self.lists['subjects'].addItem(item)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def proc_all(self, current=None, previous=None, item=None):
        """GUI calls current and previous. You can call item"""

        if item is None:
            # when clicking on a previously selected list, it sends a signal where current is None, but I don't understand why
            if current is None:
                return
            item = current.data(Qt.UserRole)

        if item.t == 'subject':
            self.list_sessions_and_protocols(item)

        elif item.t == 'session':
            self.list_runs(item)

        elif item.t == 'protocol':
            pass

        elif item.t == 'run':
            self.list_recordings(item)

        elif item.t == 'recording':
            pass

        self.list_params()
        self.list_files()

    def list_sessions_and_protocols(self, subj):

        for l in ('sessions', 'protocols', 'runs', 'recordings'):
            self.lists[l].clear()

        for sess in subj.list_sessions():
            if sess.start_time is None:
                date_str = 'unknown date'
            else:
                date_str = f'{sess.start_time:%d %b %Y}'
            item = QListWidgetItem_time(sess, f'{sess.name} ({date_str})')
            if sess.id in self.search.sessions:
                highlight(item)
            self.lists['sessions'].addItem(item)
        self.lists['sessions'].setCurrentRow(0)

        for protocol in subj.list_protocols():
            item = QListWidgetItem(protocol.METC)
            item.setData(Qt.UserRole, protocol)
            self.lists['protocols'].addItem(item)
        self.lists['protocols'].setCurrentRow(0)

    def list_runs(self, sess):

        for l in ('runs', 'recordings'):
            self.lists[l].clear()

        for run in sess.list_runs():
            item = QListWidgetItem_time(run, f'{run.task_name}')
            if run.id in self.search.runs:
                highlight(item)
            self.lists['runs'].addItem(item)
        self.lists['runs'].setCurrentRow(0)

    def list_recordings(self, run):

        self.lists['recordings'].clear()

        for recording in run.list_recordings():
            item = QListWidgetItem(recording.modality)
            item.setData(Qt.UserRole, recording)
            if recording.id in self.search.recordings:
                highlight(item)
            self.lists['recordings'].addItem(item)
        self.lists['recordings'].setCurrentRow(0)

    def list_params(self):

        self.t_params.blockSignals(True)
        self.t_params.clearContents()

        all_params = []
        for k, v in self.lists.items():
            item = v.currentItem()
            if item is None:
                continue
            obj = item.data(Qt.UserRole)

            parameters = {}

            parameters.update(table_widget(TABLES[k], obj, self))

            if k == 'subjects':
                pass

            elif k == 'protocols':
                pass

            elif k == 'sessions':

                if obj.name == 'IEMU':
                    parameters.update(table_widget(TABLES[k]['subtables']['sessions_iemu'], obj, self))

                elif obj.name == 'OR':
                    parameters.update(table_widget(TABLES[k]['subtables']['sessions_or'], obj, self))

                elif obj.name == 'MRI':
                    parameters.update(table_widget(TABLES[k]['subtables']['sessions_mri'], obj, self))

            elif k == 'runs':

                w = Popup_Experimenters(obj, self)
                parameters.update({'Experimenters': w})

                if obj.task_name == 'mario':
                    parameters.update(table_widget(TABLES[k]['subtables']['runs_mario'], obj, self))

                if obj.task_name == 'motor':
                    parameters.update(table_widget(TABLES[k]['subtables']['runs_motor'], obj, self))

            elif k == 'recordings':

                if obj.modality == 'ieeg':
                    parameters.update(table_widget(TABLES[k]['subtables']['recordings_ieeg'], obj, self))

                if obj.modality in ('bold', 'epi'):
                    parameters.update(table_widget(TABLES[k]['subtables']['recordings_epi'], obj, self))

                if obj.run.session.name == 'MRI':
                    parameters.update(table_widget(TABLES[k]['subtables']['recordings_mri'], obj, self))

            for p_k, p_v in parameters.items():
                # p_v.setEnabled(False)
                all_params.append({
                    'level': self.groups[k].title(),
                    'parameter': p_k,
                    'value': p_v,
                    })

        self.t_params.setRowCount(len(all_params))

        for i, val in enumerate(all_params):
            item = QTableWidgetItem(val['level'])
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setBackground(QBrush(QColor('lightGray')))
            self.t_params.setItem(i, 0, item)
            item = QTableWidgetItem(val['parameter'])
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.t_params.setItem(i, 1, item)
            item = QTableWidgetItem(str(val['value']))
            self.t_params.setCellWidget(i, 2, val['value'])

        self.t_params.blockSignals(False)

    def current(self, level):
        assert level in LEVELS

        item = self.lists[level].currentItem()
        if item is not None:
            return item.data(Qt.UserRole)

    def list_files(self):

        self.t_files.blockSignals(True)
        self.t_files.clearContents()

        all_files = []
        for k, v in self.lists.items():
            item = v.currentItem()
            if item is None:
                continue
            obj = item.data(Qt.UserRole)
            for file in obj.list_files():
                all_files.append({
                    'level': self.groups[k].title(),
                    'format': file.format,
                    'path': file.path,
                    'obj': [obj, file],
                    })

        self.t_files.setRowCount(len(all_files))

        for i, val in enumerate(all_files):

            item = QTableWidgetItem(val['level'])
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setBackground(QBrush(QColor('lightGray')))
            item.setData(Qt.UserRole, val['obj'])
            self.t_files.setItem(i, 0, item)

            item = QTableWidgetItem(val['format'])
            item.setData(Qt.UserRole, val['obj'])
            self.t_files.setItem(i, 1, item)

            item = QTableWidgetItem(str(val['path']))
            try:
                path_exists = val['path'].exists()

            except PermissionError as err:
                lg.warning(err)
                item.setForeground(QBrush(QColor('orange')))

            else:
                if not path_exists:
                    item.setForeground(QBrush(QColor('red')))

            item.setData(Qt.UserRole, val['obj'])
            self.t_files.setItem(i, 2, item)

        self.t_files.blockSignals(False)

    def changed(self, obj, value, x):
        if isinstance(x, QDate):
            x = repr(x.toPyDate())
        elif isinstance(x, QDateTime):
            x = repr(x.toPyDateTime())
        else:
            if isinstance(x, QLineEdit):
                x = x.text()

            x = f'{x}'

        setattr(obj, value, x)
        cmd = f'{repr(obj)}.{value} = {x}'
        self.journal.add(cmd)

    def exporting(self, checked=None, subj=None, sess=None, run=None):

        if subj is None:
            subj = self.lists['subjects'].currentItem().data(Qt.UserRole)
            sess = self.lists['sessions'].currentItem().data(Qt.UserRole)
            run = self.lists['runs'].currentItem().data(Qt.UserRole)

        d = {}
        d['subjects'] = subj.code
        if sess.name == 'MRI':
            d['sessions'] = f'{sess.name} ({sess.MagneticFieldStrength})'
        else:
            d['sessions'] = sess.name
        d['run_id'] = run.id
        d['runs'] = f'{run.task_name}'
        d['start_time'] = f'{run.start_time:%d %b %Y %H:%M:%S}'
        self.exports.append(d)

        self.list_exports()

    def clear_export(self):
        self.exports = []
        self.list_exports()

    def list_exports(self):

        self.t_export.clearContents()
        n_exports = len(self.exports)

        self.t_export.setRowCount(n_exports)

        for i, l in enumerate(self.exports):
            item = QTableWidgetItem(l['subjects'])
            self.t_export.setItem(i, 0, item)
            item = QTableWidgetItem(l['sessions'])
            self.t_export.setItem(i, 1, item)
            item = QTableWidgetItem(l['runs'])
            self.t_export.setItem(i, 2, item)
            item = QTableWidgetItem(l['start_time'])
            self.t_export.setItem(i, 3, item)

    def rightclick_list(self, pos, level=None):
        item = self.lists[level].itemAt(pos)

        menu = QMenu(self)
        if item is None:
            action = QAction(f'Add {level}', self)
            action.triggered.connect(lambda x: self.new_item(level=level))
            menu.addAction(action)

        else:
            obj = item.data(Qt.UserRole)

            action_delete = QAction('Delete', self)
            action_delete.triggered.connect(lambda x: self.delete_item(obj))
            menu.addAction(action_delete)

        menu.popup(self.lists[level].mapToGlobal(pos))

    def delete_item(self, item):
        item.delete()

        if item.t == 'subject':
            self.list_subjects()

        elif item.t == 'session':
            self.list_sessions_and_protocols(item)

        elif item.t == 'protocol':
            self.list_sessions_and_protocols(item)

        elif item.t == 'run':
            self.list_runs(item)

        elif item.t == 'recording':
            self.list_recordings(item)

        self.list_params()
        self.list_files()

    def rightclick_files(self, pos):
        item = self.t_files.itemAt(pos)

        if item is None:
            menu = QMenu(self)
            action = QAction(f'Add File', self)
            action.triggered.connect(lambda x: self.new_file(self))
            menu.addAction(action)
            menu.popup(self.t_files.mapToGlobal(pos))

        else:
            level_obj, file_obj = item.data(Qt.UserRole)
            file_path = file_obj.path.resolve()
            url_file = QUrl(str(file_path))
            url_directory = QUrl(str(file_path.parent))

            action_edit = QAction('Edit File', self)
            action_edit.triggered.connect(lambda x: self.edit_file(file_obj))
            action_openfile = QAction('Open File', self)
            action_openfile.triggered.connect(lambda x: QDesktopServices.openUrl(url_file))
            action_opendirectory = QAction('Open Containing Folder', self)
            action_opendirectory.triggered.connect(lambda x: QDesktopServices.openUrl(url_directory))
            action_delete = QAction('Delete', self)
            action_delete.triggered.connect(lambda x: self.delete_file(level_obj, file_obj))

            menu = QMenu('File Information', self)
            menu.addAction(action_edit)
            menu.addAction(action_openfile)
            menu.addAction(action_opendirectory)
            menu.addSeparator()
            menu.addAction(action_delete)
            menu.popup(self.t_files.mapToGlobal(pos))

    def sql_search(self):

        text, ok = QInputDialog.getText(
            self,
            'Search the database',
            'WHERE statement' + ' ' * 200,
            QLineEdit.Normal,
            self.search.previous,
            )

        if ok and text != '':
            self.search = Search(text)
            self.list_subjects()

    def sql_search_clear(self):
        self.search.clear()
        self.list_subjects()

    def add_search_results_to_export(self):

        for subj_id, sess_id, run_id in zip(self.search.subjects, self.search.sessions, self.search.runs):
            self.exporting(
                subj=Subject(id=subj_id),
                sess=Session(id=sess_id),
                run=Run(id=run_id),
                )

    def do_export(self, checked=None):

        subset = {'subjects': [], 'sessions': [], 'runs': []}
        run_ids = '(' + ', '.join([str(x['run_id']) for x in self.exports]) + ')'
        query = QSqlQuery(f"""\
            SELECT subjects.id, sessions.id, runs.id FROM runs
            JOIN sessions ON sessions.id == runs.session_id
            JOIN subjects ON subjects.id == sessions.subject_id
            WHERE runs.id IN {run_ids}
            """)

        while query.next():
            subset['subjects'].append(query.value(0))
            subset['sessions'].append(query.value(1))
            subset['runs'].append(query.value(2))

        data_path = QFileDialog.getExistingDirectory()
        if data_path == '':
            return
        create_bids(Path(data_path), deface=False, subset=subset)
        lg.warning('export finished')

    def new_item(self, checked=None, level=None):

        if level == 'subjects':
            text, ok = QInputDialog.getText(
                self,
                'Add New Subject',
                'Subject Code:',
                )

        elif level == 'sessions':
            current_subject = self.current('subjects')
            text, ok = QInputDialog.getItem(
                self,
                'Add New Session for {current_subject.code}',
                'Session Name:',
                TABLES['sessions']['name']['values'],
                0, False)

        elif level == 'protocol':
            current_subject = self.current('subjects')
            text, ok = QInputDialog.getItem(
                self,
                'Add New Protocol for {current_subject.code}',
                'Protocol Name:',
                TABLES['protocols']['name']['values'],
                0, False)

        elif level == 'runs':
            current_session = self.current('sessions')

            text, ok = QInputDialog.getItem(
                self,
                'Add New Run for {current_session.name}',
                'Task Name:',
                TABLES['runs']['task_name']['values'],
                0, False)

        elif level == 'recordings':
            current_run = self.current('runs')

            text, ok = QInputDialog.getItem(
                self,
                'Add New Recording for {current_run.task_name}',
                'Modality:',
                TABLES['recordings']['modality']['values'],
                0, False)

        if ok and text != '':
            if level == 'subjects':
                Subject.add(text.strip())
                self.journal.add(f'Subject.add("{text.strip()}")')
                self.list_subjects()

            elif level == 'sessions':
                current_subject.add_session(text)
                self.journal.add(f'{repr(current_subject)}.add_session("{text}")')
                self.list_sessions_and_protocols(current_subject)

            elif level == 'protocol':
                current_subject.add_protocol(text)
                self.journal.add(f'{repr(current_subject)}.add_protocol("{text}")')
                self.list_sessions_and_protocols(current_subject)

            elif level == 'runs':
                current_session.add_run(text)
                self.journal.add(f'{repr(current_session)}.add_run("{text}")')
                self.list_runs(current_session)

            elif level == 'recordings':
                current_run.add_recording(text)
                self.journal.add(f'{repr(current_run)}.add_recording("{text}")')
                self.list_recordings(current_run)

    def new_file(self, checked):
        get_new_file = NewFile(self)
        result = get_new_file.exec()

        if result:
            print(get_new_file.level.currentText())
            print(get_new_file.filepath.text())
            print(get_new_file.format.currentText())

    def edit_file(self, file_obj):
        get_new_file = NewFile(self, file_obj)
        result = get_new_file.exec()

        if result:
            print(get_new_file.level.currentText())
            print(get_new_file.filepath.text())
            print(get_new_file.format.currentText())

    def delete_file(self, level_obj, file_obj):
        level_obj.delete(file_obj)

    def closeEvent(self, event):
        settings.setValue('window/geometry', self.saveGeometry())
        settings.setValue('window/state', self.saveState())
        self.journal.close()

        event.accept()


def table_widget(table, obj, parent=None):

    d = {}
    for v in table:
        if v.endswith('id') or v == 'subtables' or v == 'when':
            continue

        item = table[v]
        value = getattr(obj, v)

        if item['type'].startswith('DATETIME'):
            w = make_datetime(item, value)
            w.dateTimeChanged.connect(partial(parent.changed, obj, v))

        elif item['type'].startswith('DATE'):
            w = make_date(item, value)
            w.dateChanged.connect(partial(parent.changed, obj, v))

        elif item['type'].startswith('FLOAT'):
            w = make_float(item, value)
            w.valueChanged.connect(partial(parent.changed, obj, v))

        elif item['type'].startswith('INTEGER'):
            w = make_integer(item, value)
            w.valueChanged.connect(partial(parent.changed, obj, v))

        elif item['type'].startswith('TEXT'):
            if 'values' in item:
                w = make_combobox(item, value)
                w.currentTextChanged.connect(partial(parent.changed, obj, v))
            else:
                w = make_edit(item, value)
                w.returnPressed.connect(partial(parent.changed, obj, v, w))

        else:
            raise ValueError(f'unknown type "{item["type"]}"')

        if 'doc' in item:
            w.setToolTip(item['doc'])

        d[item['name']] = w

    return d


def make_edit(table, value):
    w = QLineEdit()
    w.insert(value)
    return w


def make_integer(table, value):
    w = QSpinBox()
    w.setRange(-500, 500)

    if value is None:
        w.setValue(0)
        palette = QPalette()
        palette.setColor(QPalette.Text, Qt.red)
        w.setPalette(palette)

    else:
        w.setValue(value)

    return w


def make_float(table, value):
    w = QDoubleSpinBox()
    w.setRange(-500, 500)

    if value is None:
        w.setValue(0)
        palette = QPalette()
        palette.setColor(QPalette.Text, Qt.red)
        w.setPalette(palette)

    else:
        try:
            w.setValue(value)
        except TypeError:
            print(value)
            print(type(value))

    return w


def make_combobox(table, value):
    w = QComboBox()
    values = ['Unknown / Unspecified', ] + table['values']
    w.addItems(values)
    w.setCurrentText(value)

    return w


def make_date(table, value):
    w = QDateEdit()
    w.setCalendarPopup(True)
    w.setDisplayFormat('dd MMM yyyy')
    if value is None:
        w.setDate(date(1900, 1, 1))
        palette = QPalette()
        palette.setColor(QPalette.Text, Qt.red)
        w.setPalette(palette)
    else:
        w.setDate(value)

    return w


def make_datetime(table, value):
    w = QDateTimeEdit()
    w.setCalendarPopup(True)
    w.setDisplayFormat('dd MMM yyyy HH:mm:ss')
    if value is None:
        w.setDateTime(datetime(1900, 1, 1, 0, 0, 0))
        palette = QPalette()
        palette.setColor(QPalette.Text, Qt.red)
        w.setPalette(palette)
    else:
        w.setDateTime(value)

    return w


def copy_to_clipboard(text):

    clipboard = QGuiApplication.clipboard()
    clipboard.setText(text)


def highlight(item):
    item.setBackground(Qt.yellow)
    font = item.font()
    font.setBold(True)
    item.setFont(font)


class QListWidgetItem_time(QListWidgetItem):
    def __init__(self, obj, title):
        self.obj = obj
        super().__init__(title)
        self.setData(Qt.UserRole, obj)

    def __lt__(self, other):
        return self.obj.start_time < other.obj.start_time
