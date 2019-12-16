from PyQt5.QtWidgets import (
    QGroupBox,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidgetItem,
    QMainWindow,
    QWidget,
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
        self.l_runs.itemClicked.connect(self.list_recordings)

        self.l_recs = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.l_recs)
        b_recording.setLayout(layout)
        self.l_recs.itemClicked.connect(self.list_files)

        self.l_files = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.l_files)
        b_file.setLayout(layout)

        layout = QHBoxLayout()
        layout.addWidget(b_subj)
        layout.addWidget(b_sess)
        layout.addWidget(b_run)
        layout.addWidget(b_recording)
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

    def list_sessions(self, item):
        self.l_sess.clear()
        self.l_runs.clear()
        self.l_recs.clear()
        self.l_files.clear()

        subj = item.data(Qt.UserRole)

        for sess in subj.list_sessions():
            item = QListWidgetItem(sess.name)
            item.setData(Qt.UserRole, sess)
            self.l_sess.addItem(item)

    def list_runs(self, item):
        self.l_runs.clear()
        self.l_recs.clear()
        self.l_files.clear()

        sess = item.data(Qt.UserRole)

        for run in sess.list_runs():
            item = QListWidgetItem(run.task_name)
            item.setData(Qt.UserRole, run)
            self.l_runs.addItem(item)

    def list_recordings(self, item):
        self.l_recs.clear()
        self.l_files.clear()

        run = item.data(Qt.UserRole)

        for recording in run.list_recordings():
            item = QListWidgetItem(recording.modality)
            item.setData(Qt.UserRole, recording)
            self.l_recs.addItem(item)

    def list_files(self, item):
        self.l_files.clear()

        recording = item.data(Qt.UserRole)

        for file in recording.list_files():
            item = QListWidgetItem(str(file.path))
            item.setData(Qt.UserRole, file)
            self.l_files.addItem(item)
