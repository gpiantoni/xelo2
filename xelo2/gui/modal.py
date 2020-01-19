from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    )
from PyQt5.QtCore import Qt

from ..model.structure import TABLES
from ..model.filetype import parse_filetype


class NewFile(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)

        self.level = QComboBox()
        self.level.addItems([
            'Subject',
            'Session',
            'Protocol',
            'Run',
            'Recording'
            ])
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
