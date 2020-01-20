from logging import getLogger
from pathlib import Path
from datetime import date
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
    QPalette,
    )
from PyQt5.QtCore import (
    Qt,
    pyqtSlot,
    QSettings,
    QUrl,
    )

from ..model.structure import list_subjects, TABLES, open_database
from ..bids.root import create_bids

from .actions import create_menubar
from .modal import NewFile, Popup_Experimenters


settings = QSettings("xelo2", "xelo2")
lg = getLogger(__name__)

ELECTRODES_COLUMNS = ["name", "x", "y", "z", "size", "material"]
LEVELS = [
    'subjects',
    'sessions',
    'protocols',
    'runs',
    'recordings',
    ]



class Interface(QMainWindow):

    def __init__(self, sqlite_file):
        self.sqlite_file = sqlite_file
        self.sql_commands = sqlite_file.with_suffix('.log').open('w+')

        super().__init__()

        lists = {}
        groups = {}
        for k in LEVELS:
            groups[k] = QGroupBox(k.capitalize())
            lists[k] = QListWidget()
            lists[k].currentItemChanged.connect(self.proc_all)
            layout = QVBoxLayout()
            layout.addWidget(lists[k])
            lists[k].setSortingEnabled(True)
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

        # ELECTRODES: Widget
        t_elec = QTableWidget()
        t_elec.horizontalHeader().setStretchLastSection(True)
        t_elec.setSelectionBehavior(QAbstractItemView.SelectRows)
        t_elec.setColumnCount(len(ELECTRODES_COLUMNS))
        t_elec.setHorizontalHeaderLabels(ELECTRODES_COLUMNS)

        # EXPORT: Widget
        w_export = QWidget()
        col_export = QVBoxLayout()

        t_export = QTableWidget()
        t_export.horizontalHeader().setStretchLastSection(True)
        t_export.setSelectionBehavior(QAbstractItemView.SelectRows)
        t_export.setColumnCount(4)
        t_export.setHorizontalHeaderLabels(['Subject', 'Session', 'Run', 'Recording'])
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

        # electrodes
        dockwidget = QDockWidget('Electrodes', self)
        dockwidget.setWidget(t_elec)
        dockwidget.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        dockwidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        dockwidget.setObjectName('dock_elec')  # savestate
        self.addDockWidget(Qt.RightDockWidgetArea, dockwidget)

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
        self.t_elec = t_elec
        self.t_export = t_export
        self.exports = []

        create_menubar(self)

        self.access_db()
        self.show()

    def access_db(self):
        """This is where you access the database
        """
        self.sql, self.cur = open_database(self.sqlite_file)
        self.list_subjects()

    def list_subjects(self):
        for l in self.lists.values():
            l.clear()

        for subj in list_subjects(self.cur):
            item = QListWidgetItem(subj.code)
            item.setData(Qt.UserRole, subj)
            self.lists['subjects'].addItem(item)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def proc_all(self, current, previous):

        # when clicking on a previously selected list, it sends a signal where current is None, but I don't understand why
        if current is None:
            return

        item = current.data(Qt.UserRole)
        if item.t == 'subject':
            self.list_sessions_and_protocols(item)

        elif item.t == 'session':
            self.list_runs(item)
            self.show_electrodes(item)

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

        protocols = []
        for sess in subj.list_sessions():
            item = QListWidgetItem_time(sess, f'{sess.name} ({sess.start_time:%d %b %Y})')
            self.lists['sessions'].addItem(item)
            protocols.extend(sess.list_protocols())
        self.lists['sessions'].setCurrentRow(0)

        for protocol in set(protocols):
            item = QListWidgetItem(protocol.METC)
            item.setData(Qt.UserRole, protocol)
            self.lists['protocols'].addItem(item)
        self.lists['protocols'].setCurrentRow(0)

    def list_runs(self, sess):

        for l in ('runs', 'recordings'):
            self.lists[l].clear()

        for run in sess.list_runs():
            item = QListWidgetItem_time(run, f'{run.task_name}')
            self.lists['runs'].addItem(item)
        self.lists['runs'].setCurrentRow(0)

        self.list_recordings(run)

    def show_electrodes(self, sess):
        self.cur.execute(f"""\
            SELECT name, x, y, z, size, material FROM electrodes
            WHERE session_id == {sess.id}
        """)
        val = self.cur.fetchall()

        self.t_elec.clearContents()
        self.t_elec.setRowCount(len(val))

        for i_row, v in enumerate(val):
            for i_col, name in enumerate(ELECTRODES_COLUMNS):
                item = QTableWidgetItem(str(v[i_col]))
                self.t_elec.setItem(i_row, i_col, item)

    def list_recordings(self, run):

        self.lists['recordings'].clear()

        for recording in run.list_recordings():
            item = QListWidgetItem(recording.modality)
            item.setData(Qt.UserRole, recording)
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
        if isinstance(x, QLineEdit):
            x = x.text()

        cmd = f'{repr(obj)}.{value} = "{x}"'
        print(cmd)
        self.sql_commands.write(cmd + '\n')

    def exporting(self):
        """TODO"""

        d = {}
        subj = self.lists['subjects'].currentItem().data(Qt.UserRole)
        d['subjects'] = subj.code
        sess = self.lists['sessions'].currentItem().data(Qt.UserRole)
        d['sessions'] = sess.name
        run = self.lists['runs'].currentItem().data(Qt.UserRole)
        d['runs'] = f'{run.task_name} ({run.acquisition})'
        rec = self.lists['recordings'].currentItem().data(Qt.UserRole)
        d['recordings'] = rec.modality
        d['recording'] = rec.id
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
            item = QTableWidgetItem(l['recordings'])
            self.t_export.setItem(i, 3, item)

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

    def do_export(self):
        recording_ids = '(' + ', '.join([str(x['recording']) for x in self.exports]) + ')'
        self.cur.execute(f"""\
            SELECT subjects.id, sessions.id, runs.id, recordings.id FROM recordings
            JOIN runs ON runs.id == recordings.run_id
            JOIN sessions ON sessions.id == runs.session_id
            JOIN subjects ON subjects.id == sessions.subject_id
            WHERE recordings.id IN {recording_ids}
            """)
        subset = self.cur.fetchall()

        data_path = QFileDialog.getExistingDirectory()
        if data_path == '':
            return
        create_bids(Path(data_path), cur=self.cur, deface=False, subset=subset)
        lg.warning('export finished')

    def new_subject(self, checked):
        print(checked)

    def new_session(self, checked):
        print(checked)

    def new_protocol(self, checked):
        print(checked)

    def new_run(self, checked):
        print(checked)

    def new_recording(self, checked):
        print(checked)

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
        self.sql_commands.close()

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
        w.setValue(value)

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
        w.setDateTime(date(1900, 1, 1))
        palette = QPalette()
        palette.setColor(QPalette.Text, Qt.red)
        w.setPalette(palette)
    else:
        w.setDateTime(value)

    return w


class QListWidgetItem_time(QListWidgetItem):
    def __init__(self, obj, title):
        self.obj = obj
        super().__init__(title)
        self.setData(Qt.UserRole, obj)

    def __lt__(self, other):
        return self.obj.start_time < other.obj.start_time
