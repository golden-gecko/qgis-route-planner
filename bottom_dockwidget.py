from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis.PyQt.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout
from qgis.PyQt.QtGui import QPixmap, QTextCursor


class BottomDockWidget(QtWidgets.QDockWidget):
    """Dock widget placed at the bottom of the QGIS window.

    Contains a label, a read-only text area for status messages, and a horizontal
    scroll area for Street View thumbnails.
    """

    def __init__(self, parent=None):
        super(BottomDockWidget, self).__init__(parent)

        self.setWindowTitle('RoutePlanner - Bottom')

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.label = QLabel('Status', container)
        self.text = QTextEdit(container)
        self.text.setReadOnly(True)
        self.text.setFixedHeight(60)

        # thumbnails scroll area
        self.scroll = QScrollArea(container)
        self.scroll.setWidgetResizable(True)
        self.thumb_container = QWidget()
        self.thumb_layout = QHBoxLayout(self.thumb_container)
        self.thumb_layout.setContentsMargins(2, 2, 2, 2)
        self.thumb_layout.setSpacing(6)
        self.scroll.setWidget(self.thumb_container)
        self.scroll.setFixedHeight(140)

        layout.addWidget(self.label)
        layout.addWidget(self.text)
        layout.addWidget(self.scroll)

        container.setLayout(layout)
        self.setWidget(container)

    def append_text(self, line: str):
        """Append a line of text to the text area."""
        if not line.endswith('\n'):
            line = line + '\n'
        self.text.moveCursor(QTextCursor.End)
        self.text.insertPlainText(line)
        # keep scrollbar at bottom
        self.text.verticalScrollBar().setValue(self.text.verticalScrollBar().maximum())

    def set_label(self, text: str):
        self.label.setText(text)

    def clear_thumbnails(self):
        """Remove all thumbnail widgets."""
        while self.thumb_layout.count():
            item = self.thumb_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def display_thumbnails(self, pixmaps: list):
        """Display a list of QPixmap thumbnails in the scroll area.

        Expects already-scaled QPixmaps or will scale them to thumbnail size.
        """
        self.clear_thumbnails()

        thumb_h = 120
        for pm in pixmaps:
            if pm is None or pm.isNull():
                lbl = QLabel('No image')
            else:
                lbl = QLabel()
                scaled = pm.scaledToHeight(thumb_h, Qt.TransformationMode.SmoothTransformation)
                lbl.setPixmap(scaled)
            lbl.setFixedHeight(thumb_h)
            lbl.setContentsMargins(0, 0, 0, 0)
            self.thumb_layout.addWidget(lbl)

        # add stretch to keep left-aligned
        self.thumb_layout.addStretch(1)
