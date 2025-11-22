from qgis.core import QgsLineSymbol
from qgis.PyQt.QtGui import QColor


class Symbol:
    @staticmethod
    def create_dashed_line(color: QColor) -> QgsLineSymbol:
        return QgsLineSymbol.createSimple({
            'color': color,
            'line_style': 'dash',
            'width': '0.75',
        })
