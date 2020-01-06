from logging import getLogger
from pathlib import Path
from datetime import date

from PyQt5.QtWidgets import (
    QAbstractItemView,
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
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    )
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPalette,
    )
from PyQt5.QtCore import (
    Qt,
    pyqtSlot,
    QSettings,
    )

from ..model.structure import list_subjects, TABLES
from ..bids.root import create_bids

settings = QSettings("xelo2", "xelo2")
lg = getLogger(__name__)


class Interface(QMainWindow):

    def __init__(self, cur):
        self.cur = cur
        super().__init__()

        groups = {
            'subj': QGroupBox('Subject'),
            'sess': QGroupBox('Session'),
            'metc': QGroupBox('Protocol'),
            'run': QGroupBox('Run'),
            'rec': QGroupBox('Recording'),
            }

        lists = {}
        new = {}
        for k, v in groups.items():
            lists[k] = QListWidget()
            lists[k].currentItemChanged.connect(self.proc_all)
            layout = QVBoxLayout()
            layout.addWidget(lists[k])
            new[k] = QPushButton('New ' + v.title())
            new[k].setDisabled(True)
            layout.addWidget(new[k])
            if k == 'rec':
                to_export = QPushButton('Export')
                to_export.clicked.connect(self.exporting)
                layout.addWidget(to_export)
            v.setLayout(layout)

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
        col_sessmetc.addWidget(groups['sess'])
        col_sessmetc.addWidget(groups['metc'])

        # TOP PANELS
        layout_top = QHBoxLayout()
        layout_top.addWidget(groups['subj'])
        layout_top.addLayout(col_sessmetc)
        layout_top.addWidget(groups['run'])
        layout_top.addWidget(groups['rec'])

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

        self.access_db()
        self.show()

    def access_db(self):
        """This is where you access the database
        """
        self.list_subjects()

    def list_subjects(self):
        for l in self.lists.values():
            l.clear()

        for subj in list_subjects(self.cur):
            item = QListWidgetItem(subj.code)
            item.setData(Qt.UserRole, subj)
            self.lists['subj'].addItem(item)

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

        elif item.t == 'protocol':
            pass

        elif item.t == 'run':
            self.list_recordings(item)

        elif item.t == 'recording':
            pass

        self.list_params()
        self.list_files()

    def list_sessions_and_protocols(self, subj):

        for l in ('sess', 'metc', 'run', 'rec'):
            self.lists[l].clear()

        protocols = []
        for sess in subj.list_sessions():
            item = QListWidgetItem(sess.name)
            item.setData(Qt.UserRole, sess)
            self.lists['sess'].addItem(item)
            protocols.extend(sess.list_protocols())
        self.lists['sess'].setCurrentRow(0)

        for protocol in set(protocols):
            item = QListWidgetItem(protocol.METC)
            item.setData(Qt.UserRole, protocol)
            self.lists['metc'].addItem(item)
        self.lists['metc'].setCurrentRow(0)

    def list_runs(self, sess):

        for l in ('run', 'rec'):
            self.lists[l].clear()

        for run in sess.list_runs():
            item = QListWidgetItem(f'{run.task_name} ({run.acquisition})')
            item.setData(Qt.UserRole, run)
            self.lists['run'].addItem(item)
        self.lists['run'].setCurrentRow(0)

        self.list_recordings(run)

    def list_recordings(self, run):

        self.lists['rec'].clear()

        for recording in run.list_recordings():
            item = QListWidgetItem(recording.modality)
            item.setData(Qt.UserRole, recording)
            self.lists['rec'].addItem(item)
        self.lists['rec'].setCurrentRow(0)

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
            if k == 'subj':
                for v in ('sex', 'date_of_birth'):
                    parameters.update(table_widget(TABLES['subjects'][v], getattr(obj, v)))

            elif k == 'metc':
                for v in ('date_of_signature', ):
                    parameters.update(table_widget(TABLES['protocols'][v], getattr(obj, v)))

            elif k == 'sess':
                parameters = {}

                if obj.name == 'IEMU':
                    for v in ('date_of_implantation', 'date_of_explantation'):
                        parameters.update(table_widget(TABLES['sessions']['subtables']['sessions_iemu'][v], getattr(obj, v)))

                elif obj.name == 'OR':
                    for v in ('date_of_surgery', ):
                        parameters.update(table_widget(TABLES['sessions']['subtables']['sessions_or'][v], getattr(obj, v)))

                elif obj.name == 'MRI':
                    for v in ('MagneticFieldStrength', ):
                        parameters.update(table_widget(TABLES['sessions']['subtables']['sessions_mri'][v], getattr(obj, v)))

            elif k == 'run':
                for v in ('task_name', 'acquisition', 'start_time', 'end_time'):
                    parameters.update(table_widget(TABLES['runs'][v], getattr(obj, v)))

                if obj.task_name == 'motor':
                    for v in ('body_part', 'left_right'):
                        parameters.update(table_widget(TABLES['runs']['subtables']['runs_motor'][v], getattr(obj, v)))

            for p_k, p_v in parameters.items():
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
                    })

        self.t_files.setRowCount(len(all_files))

        for i, val in enumerate(all_files):
            item = QTableWidgetItem(val['level'])
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setBackground(QBrush(QColor('lightGray')))
            self.t_files.setItem(i, 0, item)
            self.t_files.setItem(i, 1, QTableWidgetItem(val['format']))
            item = QTableWidgetItem(str(val['path']))
            try:
                path_exists = val['path'].exists()

            except PermissionError as err:
                lg.warning(err)
                item.setForeground(QBrush(QColor('orange')))

            else:
                if not path_exists:
                    item.setForeground(QBrush(QColor('red')))

            self.t_files.setItem(i, 2, item)

        self.t_files.blockSignals(False)

    def exporting(self):

        d = {}
        subj = self.lists['subj'].currentItem().data(Qt.UserRole)
        d['subj'] = subj.code
        sess = self.lists['sess'].currentItem().data(Qt.UserRole)
        d['sess'] = sess.name
        run = self.lists['run'].currentItem().data(Qt.UserRole)
        d['run'] = f'{run.task_name} ({run.acquisition})'
        rec = self.lists['rec'].currentItem().data(Qt.UserRole)
        d['rec'] = rec.modality
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
            item = QTableWidgetItem(l['subj'])
            self.t_export.setItem(i, 0, item)
            item = QTableWidgetItem(l['sess'])
            self.t_export.setItem(i, 1, item)
            item = QTableWidgetItem(l['run'])
            self.t_export.setItem(i, 2, item)
            item = QTableWidgetItem(l['rec'])
            self.t_export.setItem(i, 3, item)

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

    def closeEvent(self, event):
        settings.setValue('window/geometry', self.saveGeometry())
        settings.setValue('window/state', self.saveState())

        event.accept()


def table_widget(table, value):

    if table['type'].startswith('DATETIME'):
        d = make_datetime(table, value)

    elif table['type'].startswith('DATE'):
        d = make_date(table, value)

    elif table['type'].startswith('TEXT'):
        if 'values' in table:
            d = make_combobox(table, value)
        else:
            d = make_edit(table, value)

    else:
        raise ValueError(f'unknown type "{table["type"]}"')

    return d


def make_edit(table, value):
    w = QLineEdit()
    w.insert(value)
    d = {table['name']: w}

    return d


def make_combobox(table, value):
    w = QComboBox()
    w.addItems(table['values'])
    w.setCurrentText(value)
    d = {table['name']: w}

    return d


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
    d = {table['name']: w}

    return d


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
    d = {table['name']: w}

    return d
