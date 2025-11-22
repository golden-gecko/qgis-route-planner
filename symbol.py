from qgis.core import QgsLineSymbol, QgsMarkerSymbol, QgsSymbol
from qgis.PyQt.QtGui import QColor


class Symbol:
    @staticmethod
    def create_point(color: QColor) -> QgsSymbol:
        return QgsMarkerSymbol.createSimple({
            'color': color,
            'outline_color': color,
        })

    @staticmethod
    def create_path(color: QColor) -> QgsSymbol:
        return QgsLineSymbol.createSimple({
            'color': color,
            'line_style': 'dash',
            'width': '0.75',
        })
