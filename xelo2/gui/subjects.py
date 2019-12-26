from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAbstractItemView,
                             QComboBox,
                             QDateTimeEdit,
                             QDialog,
                             QDialogButtonBox,
                             QFileDialog,
                             QFormLayout,
                             QLabel,
                             QListWidget,
                             QListWidgetItem,
                             QPushButton,
                             QSpinBox,
                             QLineEdit,
                             QDateTimeEdit,
                             )

class Add_Subject(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('New Subject')

        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.idx_ok = bbox.button(QDialogButtonBox.Ok)
        self.idx_cancel = bbox.button(QDialogButtonBox.Cancel)
        bbox.clicked.connect(self.button_clicked)

        self.idx_code = QLineEdit()
        self.idx_dob = QDateTimeEdit()
        self.idx_dob.setDisplayFormat("yyyy-MM-dd")
        self.idx_sex = QComboBox()
        self.idx_sex.addItems(['Female', 'Male'])

        layout = QFormLayout()
        layout.addRow('Code', self.idx_code)
        layout.addRow('Date of Birth', self.idx_dob)
        layout.addRow('Sex', self.idx_sex)
        layout.addRow(bbox)

        self.setLayout(layout)

    def button_clicked(self, button):
        if button == self.idx_ok:
            self.accept()

        elif button == self.idx_cancel:
            self.reject()
