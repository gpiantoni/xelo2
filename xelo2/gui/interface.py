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
    QFont,
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
        t_params = QTableWidget()
        t_params.horizontalHeader().setStretchLastSection(True)
        t_params.setSelectionBehavior(QAbstractItemView.SelectRows)
        t_params.setColumnCount(3)
        t_params.setHorizontalHeaderLabels(['Level', 'Parameter', 'Value'])
        t_params.verticalHeader().setVisible(False)

        # PARAMETERS: Layout
        groups['params'] = QGroupBox('Parameters')
        layout = QVBoxLayout()
        layout.addWidget(t_params)
        groups['params'].setLayout(layout)

        # FILES: Widget
        t_files = QTableWidget()
        t_files.horizontalHeader().setStretchLastSection(True)
        t_files.setSelectionBehavior(QAbstractItemView.SelectRows)
        t_files.setColumnCount(3)
        t_files.setHorizontalHeaderLabels(['Level', 'Format', 'File'])
        t_files.verticalHeader().setVisible(False)

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
        self.t_params = t_params
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

            if k == 'subj':
                parameters = {
                    'Date of Birth': obj.date_of_birth,
                    'Sex': obj.sex,
                    }

            elif k == 'metc':
                parameters = {
                    'Version': obj.version,
                    'Date of Signature': obj.date_of_signature,
                    }

            elif k == 'sess':
                parameters = {}

                if obj.name == 'IEMU':
                    parameters['Date of implantation'] = obj.date_of_implantation
                    parameters['Date of explantation'] = obj.date_of_explantation

                elif obj.name == 'OR':
                    parameters['Date of surgery'] = obj.date_of_surgery

            elif k == 'run':
                parameters = {
                    'Task Name': obj.task_name,
                    'Acquisition': obj.acquisition,
                    'Start Time': obj.start_time,
                    'End Time': obj.end_time,
                    }

            else:
                parameters = {}

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
            self.t_params.setItem(i, 2, item)

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
