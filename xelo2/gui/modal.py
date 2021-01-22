from logging import getLogger
from pathlib import Path
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    )
from PyQt5.QtCore import Qt

from functools import partial
from numpy import issubdtype, floating, integer

from .utils import _protocol_name
from ..api.filetype import parse_filetype
from ..api.frontend import list_experimenters
from ..database.tables import LEVELS, lookup_allowed_values
from ..io.ephys import read_info_from_ephys

lg = getLogger(__name__)


class NewFile(QDialog):

    def __init__(self, parent, file_obj=None, level_obj=None, filename=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)

        self.level = QComboBox()
        self.level.addItems([level[:-1].capitalize() for level in LEVELS])

        if level_obj is not None:
            self.level.setEnabled(False)  # do not allow changing level here
            self.level.setCurrentText(level_obj.t.capitalize())

        self.filepath = QLineEdit()
        self.filepath.setFixedWidth(800)
        self.filepath.editingFinished.connect(self.set_filetype)
        browse = QPushButton('Browse ...')
        browse.clicked.connect(self.browse)
        self.format = QComboBox()
        self.format.addItems(['Unknown', ] + lookup_allowed_values(parent.db['db'], 'files', 'format'))

        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)

        layout_file = QHBoxLayout()
        layout_file.addWidget(self.filepath)
        layout_file.addWidget(browse)

        layout = QVBoxLayout()
        layout.addWidget(self.level)
        layout.addLayout(layout_file)
        layout.addWidget(self.format)
        layout.addWidget(bbox)

        self.setLayout(layout)

        if file_obj is not None:
            # self.level.setCurrentText(file_obj)
            self.filepath.setText(str(file_obj.path))
            self.format.setCurrentText(file_obj.format)

        if filename is not None:
            self.filepath.setText(filename)
            self.set_filetype()
            self.filepath.setEnabled(False)
            self.set_filetype(filename)

    def browse(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select File')

        if filename:
            self.filepath.setText(filename)
            self.set_filetype(filename)

    def set_filetype(self, filename=None):
        if filename is None:
            filename = Path(self.filepath.text()).resolve()

        try:
            filetype = parse_filetype(filename)

        except ValueError as err:
            lg.debug(err)
            print(err)

        else:
            self.format.setCurrentText(filetype)


class EditElectrodes(QDialog):

    def __init__(self, parent, data):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)

        self.parameter = QComboBox()
        for n in data.dtype.names:
            if n in ('name', 'x', 'y', 'z'):
                continue
            self.parameter.addItem(n)

        self.value = QLineEdit()
        self.value.setFixedWidth(800)

        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)

        layout_file = QHBoxLayout()
        layout_file.addWidget(self.parameter)
        layout_file.addWidget(self.value)

        layout = QVBoxLayout()
        layout.addLayout(layout_file)
        layout.addWidget(bbox)

        self.setLayout(layout)


def _prepare_values(run, info):
    run_duration = run.duration
    if run_duration is None:
        run_duration = 0

    VALUES = [
        [
            '',
            'Current Values',
            'Imported Values'
        ],
        [
            'Start Time',
            strftime(run.start_time),
            strftime(info['start_time']),
        ],
        [
            'Duration',
            f'{run_duration:.3f} s',
            f'{info["duration"]:.3f} s',
        ],
        [
            '# Events',
            f'{len(run.events)}',
            f'{len(info["events"])}',
            ],
        ]

    return VALUES


def strftime(t):
    """This is the most accurate way to get milliseconds, without microseconds"""
    if t is None:
        return '(null)'
    else:
        return f'{t:%d/%m/%Y %H:%M:%S}.{t.microsecond / 1000:03.0f}'


class CompareEvents(QDialog):
    def __init__(self, parent, run, ephys_file):
        super().__init__(parent)

        self.info = read_info_from_ephys(parent.db, ephys_file)

        layout = QGridLayout(self)

        VALUES = _prepare_values(run, self.info)
        for i0, vals in enumerate(VALUES):
            for i1, value in enumerate(vals):
                label = QLabel(value)
                label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                layout.addWidget(label, i0, i1)

        layout.addWidget(make_table(run.events), i0 + 1, 1)
        layout.addWidget(make_table(self.info['events']), i0 + 1, 2)

        self.old = QPushButton('Keep old events')
        self.old.clicked.connect(self.reject)
        self.new = QPushButton('Use new events')
        self.new.clicked.connect(self.accept)
        layout.addWidget(self.old, i0 + 2, 1)
        layout.addWidget(self.new, i0 + 2, 2)

        self.setLayout(layout)


def make_table(ev):
    t0 = QTableWidget()
    t0.horizontalHeader().setStretchLastSection(True)
    t0.setColumnCount(len(ev.dtype.names))
    t0.setHorizontalHeaderLabels(ev.dtype.names)
    t0.verticalHeader().setVisible(False)
    n_rows = min(len(ev), 10)
    t0.setRowCount(n_rows)

    for i0, name in enumerate(ev.dtype.names):
        for i1 in range(n_rows):
            v = ev[name][i1]

            if issubdtype(ev.dtype[name].type, floating):
                v = f'{v:.3f}'

            elif issubdtype(ev.dtype[name].type, integer):
                v = f'{v}'

            item = QTableWidgetItem(v)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            t0.setItem(i1, i0, item)

    table = t0
    table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    table.resizeColumnsToContents()
    table.setFixedSize(
        table.horizontalHeader().length() + table.verticalHeader().width(),
        table.verticalHeader().length() + table.horizontalHeader().height())

    return t0


class Popup_Experimenters(QPushButton):

    def __init__(self, run, parent):
        self.run = run
        super().__init__(parent)
        self.set_title()

        self.menu = QMenu(self)
        current_experimenters = run.experimenters
        for name in list_experimenters(parent.db):
            action = QAction(name, self)
            action.setCheckable(True)
            if name in current_experimenters:
                action.setChecked(True)
            action.toggled.connect(self.action_toggle)
            self.menu.addAction(action)
        self.setMenu(self.menu)

    def action_toggle(self, checked):

        names = []
        for action in self.menu.actions():
            if action.isChecked():
                names.append(action.text())

        self.run.experimenters = names

        self.set_title()
        self.showMenu()

    def set_title(self):
        self.setText(', '.join(self.run.experimenters))


class Popup_Protocols(QPushButton):

    def __init__(self, run, parent):
        self.run = run
        super().__init__(parent)
        self.set_title()

        subject = run.session.subject

        current_protocols = [metc.id for metc in run.list_protocols()]
        self.menu = QMenu(self)
        for metc in subject.list_protocols():
            action = QAction(_protocol_name(metc), self)
            action.setCheckable(True)
            if metc.id in current_protocols:
                action.setChecked(True)
            action.toggled.connect(partial(self.action_toggle, metc=metc))
            self.menu.addAction(action)
        self.setMenu(self.menu)

    def action_toggle(self, checked, metc):
        if checked:
            self.run.attach_protocol(metc)
        else:
            self.run.detach_protocol(metc)

        self.set_title()
        self.showMenu()

    def set_title(self):
        self.setText(', '.join(_protocol_name(x) for x in self.run.list_protocols()))


class Popup_IntendedFor(QPushButton):

    def __init__(self, run, parent):
        self.run = run
        super().__init__(parent)
        self.set_title()

        current_targets = [x.id for x in run.intendedfor]

        self.menu = QMenu(self)
        for i, one_run in enumerate(run.session.list_runs()):
            if one_run.id == run.id:
                continue
            name = f'#{i + 1: 2d}: {one_run.task_name}'
            action = QAction(name, self)
            action.setCheckable(True)
            if one_run.id in current_targets:
                action.setChecked(True)
            action.toggled.connect(partial(self.action_toggle, target=one_run))
            self.menu.addAction(action)

        self.setMenu(self.menu)

    def action_toggle(self, checked, target):

        current_targets = self.run.intendedfor
        if checked:
            current_targets.append(target)
        else:
            current_targets = [x for x in current_targets if x.id != target.id]

        self.run.intendedfor = current_targets

        self.set_title()
        self.showMenu()

    def set_title(self):
        len_intendedfor = len(self.run.intendedfor)
        if len_intendedfor == 1:
            plural = ''
        else:
            plural = 's'

        self.setText(f'({len_intendedfor} target task{plural})')


class AccessDatabase(QDialog):
    EMPTY_PUSHBUTTON = '(click to select file)'

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)

        self.db_type = QComboBox()
        self.db_type.addItems(['mysql / mariadb', 'sqlite'])
        self.db_type.currentTextChanged.connect(self.switch_dbtype)

        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)

        self.db_name = QLineEdit()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        layout = QFormLayout()
        layout.addRow('Database Name', self.db_name)
        layout.addRow('Username', self.username)
        layout.addRow('Password', self.password)
        mysql = QWidget()
        mysql.setLayout(layout)

        self.sqlite_path = QPushButton(self.EMPTY_PUSHBUTTON)
        self.sqlite_path.clicked.connect(self.select_file)
        layout = QFormLayout()
        layout.addRow('Path to Database', self.sqlite_path)
        sqlite = QWidget()
        sqlite.setLayout(layout)

        self.stacked = QStackedLayout()
        self.stacked.addWidget(mysql)
        self.stacked.addWidget(sqlite)

        layout = QVBoxLayout()
        layout.addWidget(self.db_type)
        layout.addLayout(self.stacked)
        layout.addWidget(bbox)

        self.setLayout(layout)

    def switch_dbtype(self, selected):
        if selected == 'sqlite':
            self.stacked.setCurrentIndex(1)
        else:
            self.stacked.setCurrentIndex(0)

    def select_file(self):
        out = QFileDialog.getOpenFileName(
            self,
            'Open SQLITE database',
            None,
            "SQLITE database (*.*)")[0]
        if out != '':
            self.sqlite_path.setText(out)


def parse_accessdatabase(parent):
    self = AccessDatabase(parent)
    result = self.exec()
    DB_ARGS = {}
    if result:
        if self.stacked.currentIndex() == 0:
            DB_ARGS['db_type'] = 'QMYSQL'
            db_name = self.db_name.text()
            if db_name == '':
                return None
            else:
                DB_ARGS['db_name'] = db_name
            DB_ARGS['username'] = self.username.text()
            DB_ARGS['password'] = self.password.text()
        else:
            DB_ARGS['db_type'] = 'QSQLITE'
            db_name = self.sqlite_path.text()
            if db_name == self.EMPTY_PUSHBUTTON:
                return None
            else:
                DB_ARGS['db_name'] = db_name

        return DB_ARGS
