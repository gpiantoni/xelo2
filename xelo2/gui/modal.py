from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QMenu,
    QPushButton,
    QVBoxLayout,
    )
from PyQt5.QtCore import Qt

from functools import partial

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
