from PyQt5.QtWidgets import (
    QGroupBox,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidgetItem,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QTableWidget,
    QTabWidget,
    QTableWidgetItem,
    QAbstractItemView
    )
from PyQt5.QtCore import Qt, pyqtSlot

from ..model import list_subjects


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
        b_metc = QGroupBox('Protocol')
        b_run = QGroupBox('Run')
        b_recording = QGroupBox('Recording')

        self.l_subj = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.l_subj)
        p_newsubj = QPushButton('New Subject')
        layout.addWidget(p_newsubj)
        b_subj.setLayout(layout)
        self.l_subj.currentItemChanged.connect(self.proc_subj)

        self.l_sess = QListWidget()
        self.l_sess.itemClicked.connect(self.list_runs)
        layout = QVBoxLayout()
        layout.addWidget(self.l_sess)
        b_sess.setLayout(layout)

        self.l_metc = QListWidget()
        self.l_metc.itemClicked.connect(self.proc_metc)
        layout = QVBoxLayout()
        layout.addWidget(self.l_metc)
        b_metc.setLayout(layout)

        b_sessmetc = QVBoxLayout()
        b_sessmetc.addWidget(b_sess)
        b_sessmetc.addWidget(b_metc)

        self.l_runs = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.l_runs)
        b_run.setLayout(layout)
        self.l_runs.itemClicked.connect(self.list_recordings)

        self.l_recs = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.l_recs)
        b_recording.setLayout(layout)
        self.l_recs.itemClicked.connect(self.proc_rec)

        self.w_parameters = QTabWidget()
        self.tab_subj = QTableWidget()
        self.tab_subj.horizontalHeader().setStretchLastSection(True)
        self.tab_subj.setColumnCount(2)
        self.w_parameters.addTab(self.tab_subj, 'Subject')
        self.tab_sess = QTableWidget()
        self.tab_sess.setColumnCount(2)
        self.tab_sess.horizontalHeader().setStretchLastSection(True)
        self.w_parameters.addTab(self.tab_sess, 'Session')
        self.tab_metc = QTableWidget()
        self.tab_metc.setColumnCount(2)
        self.tab_metc.horizontalHeader().setStretchLastSection(True)
        self.w_parameters.addTab(self.tab_metc, 'Protocol')
        self.tab_run = QTableWidget()
        self.tab_run.setColumnCount(2)
        self.tab_run.horizontalHeader().setStretchLastSection(True)
        self.w_parameters.addTab(self.tab_run, 'Run')
        self.tab_rec = QTableWidget()
        self.tab_rec.horizontalHeader().setStretchLastSection(True)
        self.tab_rec.setColumnCount(2)
        self.w_parameters.addTab(self.tab_rec, 'Recording')

        b_parameters = QGroupBox('Parameters')
        layout = QVBoxLayout()
        layout.addWidget(self.w_parameters)
        b_parameters.setLayout(layout)

        self.l_files = QTableWidget()
        self.l_files.horizontalHeader().setStretchLastSection(True)
        self.l_files.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.l_files.setColumnCount(3)
        self.l_files.setHorizontalHeaderLabels(['Level', 'Format', 'File'])

        b_file = QGroupBox('File')
        layout = QVBoxLayout()
        layout.addWidget(self.l_files)
        b_file.setLayout(layout)

        layout_t = QHBoxLayout()
        layout_t.addWidget(b_subj)
        layout_t.addLayout(b_sessmetc)
        layout_t.addWidget(b_run)
        layout_t.addWidget(b_recording)

        layout_d = QHBoxLayout()
        layout_d.addWidget(b_parameters)
        layout_d.addWidget(b_file)
        layout_d.setStretch(0, 1)
        layout_d.setStretch(1, 3)

        layout = QVBoxLayout()
        layout.addLayout(layout_t)
        layout.addLayout(layout_d)
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

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def proc_subj(self, current, previous):
        self.list_sessions(current)

    def list_sessions(self, item):

        subj = item.data(Qt.UserRole)

        self.tab_subj.clearContents()
        self.tab_subj.setRowCount(10)  # todo
        self.tab_subj.setItem(0, 0, QTableWidgetItem('Date Of Birth'))
        self.tab_subj.setItem(0, 1, QTableWidgetItem(str(subj.date_of_birth)))
        self.tab_subj.setItem(1, 0, QTableWidgetItem('Sex'))
        self.tab_subj.setItem(1, 1, QTableWidgetItem(subj.sex))
        i = 2
        for k, v in subj.parameters.items():
            self.tab_subj.setItem(i, 0, QTableWidgetItem(k))
            self.tab_subj.setItem(i, 1, QTableWidgetItem(str(v)))
            i += 1
        self.w_parameters.setCurrentIndex(0)

        self.l_sess.clear()
        self.l_metc.clear()
        self.l_runs.clear()
        self.l_recs.clear()

        protocols = []
        for sess in subj.list_sessions():
            item = QListWidgetItem(sess.name)
            item.setData(Qt.UserRole, sess)
            self.l_sess.addItem(item)
            protocols.extend(sess.list_protocols())

        for protocol in set(protocols):
            item = QListWidgetItem(protocol.METC)
            item.setData(Qt.UserRole, protocol)
            self.l_metc.addItem(item)

        self.add_files()

    def proc_metc(self, item):

        metc = item.data(Qt.UserRole)

        self.tab_metc.clearContents()
        self.tab_metc.setRowCount(10)  # todo
        self.tab_metc.setItem(0, 0, QTableWidgetItem('Version'))
        self.tab_metc.setItem(0, 1, QTableWidgetItem(metc.version))
        self.tab_metc.setItem(1, 0, QTableWidgetItem('Date of Signature'))
        self.tab_metc.setItem(1, 1, QTableWidgetItem(str(metc.date_of_signature)))
        i = 2
        for k, v in metc.parameters.items():
            self.tab_metc.setItem(i, 0, QTableWidgetItem(k))
            self.tab_metc.setItem(i, 1, QTableWidgetItem(str(v)))
            i += 1
        self.w_parameters.setCurrentIndex(2)

    def list_runs(self, item):

        sess = item.data(Qt.UserRole)

        self.tab_sess.clearContents()
        self.tab_sess.setRowCount(10)  # todo
        i = 0
        for k, v in sess.parameters.items():
            self.tab_sess.setItem(i, 0, QTableWidgetItem(k))
            self.tab_sess.setItem(i, 1, QTableWidgetItem(str(v)))
            i += 1
        self.w_parameters.setCurrentIndex(1)

        self.l_runs.clear()
        self.l_recs.clear()

        for run in sess.list_runs():
            item = QListWidgetItem(f'{run.task_name} ({run.acquisition})')
            item.setData(Qt.UserRole, run)
            self.l_runs.addItem(item)

        self.add_files()

    def list_recordings(self, item):
        self.l_recs.clear()

        run = item.data(Qt.UserRole)
        self.tab_run.clearContents()
        self.tab_run.setRowCount(10)  # todo
        self.tab_run.setItem(0, 0, QTableWidgetItem('Task Name'))
        self.tab_run.setItem(0, 1, QTableWidgetItem(run.task_name))
        self.tab_run.setItem(1, 0, QTableWidgetItem('Acquisition'))
        self.tab_run.setItem(1, 1, QTableWidgetItem(run.acquisition))
        self.tab_run.setItem(2, 0, QTableWidgetItem('Start Time'))
        self.tab_run.setItem(2, 1, QTableWidgetItem(str(run.start_time)))
        self.tab_run.setItem(3, 0, QTableWidgetItem('End Time'))
        self.tab_run.setItem(3, 1, QTableWidgetItem(str(run.end_time)))

        i = 4
        for k, v in run.parameters.items():
            self.tab_run.setItem(i, 0, QTableWidgetItem(k))
            self.tab_run.setItem(i, 1, QTableWidgetItem(str(v)))
            i += 1
        self.w_parameters.setCurrentIndex(3)

        for recording in run.list_recordings():
            item = QListWidgetItem(recording.modality)
            item.setData(Qt.UserRole, recording)
            self.l_recs.addItem(item)

        self.add_files()

    def proc_rec(self, item):

        recording = item.data(Qt.UserRole)

        self.tab_rec.clearContents()
        self.tab_rec.setRowCount(10)  # todo
        i = 0
        for k, v in recording.parameters.items():
            self.tab_rec.setItem(i, 0, QTableWidgetItem(k))
            self.tab_rec.setItem(i, 1, QTableWidgetItem(str(v)))
            i += 1
        self.w_parameters.setCurrentIndex(4)

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
                self.l_files.setItem(i, 1, QTableWidgetItem(file.format))
                self.l_files.setItem(i, 2, QTableWidgetItem(str(file.path)))
                i += 1

        item = self.l_sess.currentItem()
        if item is not None:
            sess = item.data(Qt.UserRole)
            for file in sess.list_files():
                self.l_files.setItem(i, 0, QTableWidgetItem('session'))
                self.l_files.setItem(i, 1, QTableWidgetItem(file.format))
                self.l_files.setItem(i, 2, QTableWidgetItem(str(file.path)))
                i += 1

        item = self.l_runs.currentItem()
        if item is not None:
            run = item.data(Qt.UserRole)
            for file in run.list_files():
                self.l_files.setItem(i, 0, QTableWidgetItem('run'))
                self.l_files.setItem(i, 1, QTableWidgetItem(file.format))
                self.l_files.setItem(i, 2, QTableWidgetItem(str(file.path)))
                i += 1

        item = self.l_recs.currentItem()
        if item is not None:
            recording = item.data(Qt.UserRole)
            for file in recording.list_files():
                self.l_files.setItem(i, 0, QTableWidgetItem('recording'))
                self.l_files.setItem(i, 1, QTableWidgetItem(file.format))
                self.l_files.setItem(i, 2, QTableWidgetItem(str(file.path)))
                i += 1

        self.l_files.blockSignals(False)
