from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    )
from PyQt5.QtCore import Qt

from functools import partial
from wonambi import Dataset
from numpy import issubdtype, floating, integer, empty

from ..database import TABLES
from .utils import LEVELS, _protocol_name
from ..api.filetype import parse_filetype


class NewFile(QDialog):

    def __init__(self, parent, file_obj=None, level_obj=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)

        self.level = QComboBox()
        self.level.addItems([level[:-1].capitalize() for level in LEVELS])

        if level_obj is not None:
            self.level.setEnabled(False)  # do not allow changing level here
            self.level.setCurrentText(level_obj.t.capitalize())

        self.filepath = QLineEdit()
        self.filepath.setFixedWidth(800)
        browse = QPushButton('Browse ...')
        browse.clicked.connect(self.browse)
        self.format = QComboBox()
        self.format.addItems(['Unknown', ] + TABLES['files']['format']['values'])

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

    def browse(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select File')

        if filename:
            self.filepath.setText(filename)

            try:
                filetype = parse_filetype(filename)

            except ValueError as err:
                print(err)

            else:
                self.format.setCurrentText(filetype)


def _read_info_from_ieeg(path_to_file, dtypes):
    """This could go to xelo2/io"""

    if path_to_file.suffix == '.nev':  # ns3 has more information (f.e. n_samples when there are no triggers)
        path_to_file = path_to_file.with_suffix('.ns3')

    d = Dataset(path_to_file)
    mrk = d.read_markers()

    ev = empty(len(mrk), dtype=dtypes)
    ev['onset'] = [x['start'] for x in mrk]
    ev['duration'] = [x['start'] for x in mrk]
    ev['value'] = [x['name'] for x in mrk]

    info = {
        'start_time': d.header['start_time'],
        'duration': d.header['n_samples'] / d.header['s_freq'],
        'events': ev
        }
    return info


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
            str(run.start_time),
            str(info['start_time']),
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


class CompareEvents(QDialog):
    def __init__(self, parent, run, ieeg_file):
        super().__init__(parent)

        self.info = _read_info_from_ieeg(ieeg_file, run.events.dtype)

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
        for name in TABLES['experimenters']['name']['values']:
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
