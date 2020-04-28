from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    )

from PyQt5.QtSql import QSqlQuery
from PyQt5.QtCore import Qt

from ..database import TABLES


def show_summary(parent):
    s = Summary(parent)
    s.run()


class Summary(QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        lay = QFormLayout()
        lay.addRow(
            '# Subjects',
            _info('SELECT COUNT(id) FROM subjects'))
        for session_name in TABLES['sessions']['name']['values']:
            lay.addRow(
                f'# Subjects with {session_name} session',
                _info(f'SELECT COUNT(DISTINCT subject_id) FROM sessions WHERE name == "{session_name}"'))
        lay.addRow(
            f'# Subjects with both MRI and IEMU sessions',
            _info("""
                SELECT COUNT(id) FROM subjects
                WHERE subjects.id in (SELECT subject_id FROM sessions WHERE sessions.name == 'IEMU')
                AND subjects.id in (SELECT subject_id FROM sessions WHERE sessions.name == 'MRI')"""))
        lay.addRow(
            '# Runs',
            _info('SELECT COUNT(id) FROM runs'))
        lay.addRow(
            '# Runs with events',
            _info('SELECT COUNT(id) FROM runs WHERE id IN (SELECT run_id FROM events)'))
        lay.addRow(
            '# Runs with recordings',
            _info('SELECT COUNT(DISTINCT run_id) FROM recordings'))
        lay.addRow(
            '# iEEG Recordings',
            _info('SELECT COUNT(id) FROM recordings WHERE recordings.modality == "ieeg"'))
        for chan_elec in ('channel', 'electrode'):
            lay.addRow(
                f'# iEEG Recordings with {chan_elec}s',
                _info(f"""
                    SELECT COUNT(id) FROM recordings
                    JOIN recordings_ieeg ON recordings_ieeg.recording_id == recordings.id
                    WHERE recordings.modality == "ieeg"
                    AND recordings_ieeg.{chan_elec}_group_id IS NOT NULL"""))

        ok_button = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_button.accepted.connect(self.accept)

        lay.addWidget(ok_button)
        self.setLayout(lay)

    def run(self):
        self.show()
        self.raise_()
        self.activateWindow()


def _info(s):
    query = QSqlQuery(s)
    label = QLabel()
    label.setAlignment(Qt.AlignRight)
    if query.next():
        label.setText(str(query.value(0)))
    else:
        label.setText("(ERROR)")

    return label
