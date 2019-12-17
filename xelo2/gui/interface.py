from PyQt5.QtWidgets import (
    QGroupBox,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QListWidgetItem,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView
    )
from PyQt5.QtCore import Qt

from .model import list_subjects


class Interface(QMainWindow):

    def __init__(self, cur):
        super().__init__()

        self.setCentralWidget(Main(cur))
        self.show()


class Main(QWidget):

    def __init__(self, cur):
        self.cur = cur
        super().__init__()

        b_subj = QGroupBox('Subject')
        b_sess = QGroupBox('Session')
        b_run = QGroupBox('Run')
        b_recording = QGroupBox('Recording')

        b_file = QGroupBox('File')

        self.l_subj = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.l_subj)
        layout_form = QFormLayout()
        self.subj_dob = QLabel('')
        layout_form.addRow('Date Of Birth', self.subj_dob)
        self.subj_sex = QLabel('')
        layout_form.addRow('Sex', self.subj_sex)
        layout.addLayout(layout_form)
        p_newsubj = QPushButton('New Subject')
        layout.addWidget(p_newsubj)
        b_subj.setLayout(layout)
        self.l_subj.itemClicked.connect(self.list_sessions)

        self.l_sess = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.l_sess)
        b_sess.setLayout(layout)
        self.l_sess.itemClicked.connect(self.list_runs)

        self.l_runs = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.l_runs)
        b_run.setLayout(layout)
        layout_form = QFormLayout()
        self.run_start = QLabel('')
        layout_form.addRow('Start Time', self.run_start)
        self.run_end = QLabel('')
        layout_form.addRow('End Time', self.run_end)
        layout.addLayout(layout_form)
        self.l_runs.itemClicked.connect(self.list_recordings)

        self.l_recs = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.l_recs)
        b_recording.setLayout(layout)
        self.l_recs.itemClicked.connect(self.add_files)

        self.l_files = QTableWidget()
        self.l_files.horizontalHeader().setStretchLastSection(True)
        self.l_files.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.l_files.setColumnCount(3)
        self.l_files.setHorizontalHeaderLabels(['Level', 'Type', 'File'])

        layout = QVBoxLayout()
        layout.addWidget(self.l_files)
        b_file.setLayout(layout)

        layout_g = QHBoxLayout()
        layout_g.addWidget(b_subj)
        layout_g.addWidget(b_sess)
        layout_g.addWidget(b_run)
        layout_g.addWidget(b_recording)

        layout = QVBoxLayout()
        layout.addLayout(layout_g)
        layout.addWidget(b_file)
        self.setLayout(layout)
        self.show()

        self.list_subjects()

    def list_subjects(self):
        self.l_subj.clear()

        for subj in list_subjects(self.cur):
            item = QListWidgetItem(subj.code)
            item.setData(Qt.UserRole, subj)
            self.l_subj.addItem(item)

        self.add_files()

    def list_sessions(self, item):

        subj = item.data(Qt.UserRole)
        self.subj_dob.setText(str(subj.date_of_birth))
        self.subj_sex.setText(subj.sex)

        self.l_sess.clear()
        self.l_runs.clear()
        self.l_recs.clear()

        for sess in subj.list_sessions():
            item = QListWidgetItem(sess.name)
            item.setData(Qt.UserRole, sess)
            self.l_sess.addItem(item)

        self.add_files()

    def list_runs(self, item):
        self.l_runs.clear()
        self.l_recs.clear()

        sess = item.data(Qt.UserRole)

        for run in sess.list_runs():
            item = QListWidgetItem(run.task_name)
            item.setData(Qt.UserRole, run)
            self.l_runs.addItem(item)

        self.add_files()

    def list_recordings(self, item):
        self.l_recs.clear()

        run = item.data(Qt.UserRole)
        self.run_start.setText(str(run.start_time))
        self.run_end.setText(str(run.end_time))

        for recording in run.list_recordings():
            item = QListWidgetItem(recording.modality)
            item.setData(Qt.UserRole, recording)
            self.l_recs.addItem(item)

        self.add_files()

    def add_files(self, item=None):

        self.l_files.blockSignals(True)
        self.l_files.clearContents()
        self.l_files.setRowCount(100)  # todo

        i = 0
        item = self.l_subj.currentItem()
        if item is not None:
            subj = item.data(Qt.UserRole)
            for file in subj.list_files():
                self.l_files.setItem(i, 0, QTableWidgetItem('subject'))
                self.l_files.setItem(i, 1, QTableWidgetItem(file.type))
                self.l_files.setItem(i, 2, QTableWidgetItem(str(file.path)))
                i += 1

        item = self.l_sess.currentItem()
        if item is not None:
            sess = item.data(Qt.UserRole)
            for file in sess.list_files():
                self.l_files.setItem(i, 0, QTableWidgetItem('session'))
                self.l_files.setItem(i, 1, QTableWidgetItem(file.type))
                self.l_files.setItem(i, 2, QTableWidgetItem(str(file.path)))
                i += 1

        item = self.l_runs.currentItem()
        if item is not None:
            run = item.data(Qt.UserRole)
            for file in run.list_files():
                self.l_files.setItem(i, 0, QTableWidgetItem('run'))
                self.l_files.setItem(i, 1, QTableWidgetItem(file.type))
                self.l_files.setItem(i, 2, QTableWidgetItem(str(file.path)))
                i += 1

        item = self.l_recs.currentItem()
        if item is not None:
            recording = item.data(Qt.UserRole)
            for file in recording.list_files():
                self.l_files.setItem(i, 0, QTableWidgetItem('recording'))
                self.l_files.setItem(i, 1, QTableWidgetItem(file.type))
                self.l_files.setItem(i, 2, QTableWidgetItem(str(file.path)))
                i += 1

        self.l_files.blockSignals(False)

