import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

try:
    from qgis.PyQt.QtWebEngineWidgets import QWebEngineView
except ImportError:
    QWebEngineView = None


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(str(__file__)), 'route_planner_dockwidget_base.ui'))


class RoutePlannerDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, parent = None):
        super(RoutePlannerDockWidget, self).__init__(parent)

        self.setupUi(self)
        self.streetViewBrowser = None

        if QWebEngineView is None:
            self.labelStreetView.setText('QtWebEngine is not available')
            return

        self.streetViewBrowser = QWebEngineView(self)
        self.streetViewBrowser.setMinimumHeight(220)

        index = self.gridLayout.indexOf(self.labelStreetView)

        if index < 0:
            return

        row, column, row_span, column_span = self.gridLayout.getItemPosition(index)
        self.gridLayout.removeWidget(self.labelStreetView)
        self.labelStreetView.deleteLater()
        self.gridLayout.addWidget(self.streetViewBrowser, row, column, row_span, column_span)

    def closeEvent(self, event):
        self.closingPlugin.emit()

        event.accept()
