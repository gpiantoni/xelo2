from logging import getLogger

from PyQt5.QtWidgets import (
    QGroupBox,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidgetItem,
    QMainWindow,
    QWidget,
    QPushButton,
    QTableWidget,
    QTabWidget,
    QTableWidgetItem,
    QAbstractItemView
    )
from PyQt5.QtGui import (
    QBrush,
    QColor,
    )
from PyQt5.QtCore import Qt, pyqtSlot

from ..model import list_subjects

lg = getLogger(__name__)

class Interface(QMainWindow):

    def __init__(self, cur):
        super().__init__()

        self.setCentralWidget(Main(cur))
        self.show()


class Main(QWidget):

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
            v.setLayout(layout)

        # PARAMETERS: Widget
        w_params = QTabWidget()

        params = {}
        for k, v in groups.items():
            params[k] = QTableWidget()
            params[k].horizontalHeader().setStretchLastSection(True)
            params[k].setColumnCount(2)
            params[k].setHorizontalHeaderLabels(['Parameter', 'Value'])
            params[k].verticalHeader().setVisible(False)
            w_params.addTab(params[k], v.title())

        # PARAMETERS: Layout
        groups['params'] = QGroupBox('Parameters')
        layout = QVBoxLayout()
        layout.addWidget(w_params)
        groups['params'].setLayout(layout)

        # FILES: Widget
        t_files = QTableWidget()
        t_files.horizontalHeader().setStretchLastSection(True)
        t_files.setSelectionBehavior(QAbstractItemView.SelectRows)
        t_files.setColumnCount(3)
        t_files.setHorizontalHeaderLabels(['Level', 'Format', 'File'])

        # FILES: Layout
        groups['files'] = QGroupBox('Files')
        layout = QVBoxLayout()
        layout.addWidget(t_files)
        groups['files'].setLayout(layout)

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

        # BOTTOM PANELS
        layout_bottom = QHBoxLayout()
        layout_bottom.addWidget(groups['params'])
        layout_bottom.addWidget(groups['files'])
        layout_bottom.setStretch(0, 1)
        layout_bottom.setStretch(1, 3)

        # FULL LAYOUT
        layout = QVBoxLayout()
        layout.addLayout(layout_top)
        layout.addLayout(layout_bottom)
        self.setLayout(layout)
        self.show()

        # SAVE THESE ITEMS
        self.groups = groups
        self.lists = lists
        self.params = params
        self.w_params = w_params
        self.t_files = t_files

        self.access_db()

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
            self.proc_subj(item)

        elif item.t == 'session':
            self.proc_sess(item)

        elif item.t == 'protocol':
            self.proc_metc(item)

        elif item.t == 'run':
            self.proc_run(item)

        elif item.t == 'recording':
            self.proc_rec(item)

        self.list_files()

    def proc_subj(self, subj):

        self.list_sessions_and_protocols(subj)

        parameters = {
            'Date of Birth': subj.date_of_birth,
            'Sex': subj.sex,
            }
        parameters.update(subj.parameters)

        self.show_params('subj', parameters)

    def list_sessions_and_protocols(self, subj):

        for l in ('sess', 'metc', 'run', 'rec'):
            self.lists[l].clear()

        protocols = []
        for sess in subj.list_sessions():
            item = QListWidgetItem(sess.name)
            item.setData(Qt.UserRole, sess)
            self.lists['sess'].addItem(item)
            protocols.extend(sess.list_protocols())

        for protocol in set(protocols):
            item = QListWidgetItem(protocol.METC)
            item.setData(Qt.UserRole, protocol)
            self.lists['metc'].addItem(item)

    def proc_sess(self, sess):

        self.list_runs(sess)

        self.show_params('sess', sess.parameters)

    def list_runs(self, sess):

        for l in ('run', 'rec'):
            self.lists[l].clear()

        for run in sess.list_runs():
            item = QListWidgetItem(f'{run.task_name} ({run.acquisition})')
            item.setData(Qt.UserRole, run)
            self.lists['run'].addItem(item)

    def proc_metc(self, metc):

        parameters = {
            'Version': metc.version,
            'Date of Signature': metc.date_of_signature,
            }
        parameters.update(metc.parameters)

        self.show_params('metc', parameters)

    def proc_run(self, run):

        parameters = {
            'Task Name': run.task_name,
            'Acquisition': run.acquisition,
            'Start Time': run.start_time,
            'End Time': run.end_time,
            }
        parameters.update(run.parameters)

        self.show_params('run', parameters)

        self.list_recordings(run)

    def list_recordings(self, run):

        self.lists['rec'].clear()

        for recording in run.list_recordings():
            item = QListWidgetItem(recording.modality)
            item.setData(Qt.UserRole, recording)
            self.lists['rec'].addItem(item)

    def proc_rec(self, rec):

        self.show_params('rec', rec.parameters)

    def show_params(self, tabname, parameters):

        tab = self.params[tabname]
        tab.clearContents()
        tab.setRowCount(len(parameters))

        for i, (k, v) in enumerate(parameters.items()):
            tab.setItem(i, 0, QTableWidgetItem(k))
            tab.setItem(i, 1, QTableWidgetItem(str(v)))

        self.w_params.setCurrentWidget(tab)

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
            self.t_files.setItem(i, 0, QTableWidgetItem(val['level']))
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
