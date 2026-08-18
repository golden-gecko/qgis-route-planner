from typing import Optional

from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

from .iface import Iface
from .log import log_call


class Dialog:
    @staticmethod
    @log_call
    def confirm(title: str) -> bool:
        res = QMessageBox.question(Iface.get().mainWindow(), title, title, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return res == QMessageBox.StandardButton.Yes

    @staticmethod
    @log_call
    def get_file_name() -> Optional[str]:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilters(['GPX files (*.gpx)'])

        if not dialog.exec():
            return None

        if len(dialog.selectedFiles()) != 1:
            return None

        return dialog.selectedFiles()[0]
