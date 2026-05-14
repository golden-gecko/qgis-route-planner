from qgis.core import QgsLineSymbol, QgsMarkerSymbol, QgsSymbol
from qgis.PyQt.QtGui import QColor


class Symbol:
    @staticmethod
    def create_point(color: QColor) -> QgsSymbol:
        return QgsMarkerSymbol.createSimple({
            'color': color,
            'outline_color': color,
            'size': 3,
        })

    @staticmethod
    def create_path(color: QColor) -> QgsSymbol:
        return QgsLineSymbol.createSimple({
            'color': color,
            'line_style': 'dash',
            'width': 0.75,
        })

    @staticmethod
    def create_waypoint(color: QColor) -> QgsSymbol:
        return QgsMarkerSymbol.createSimple({
            'color': color,
            'outline_color': 'black',
            'size': 3,
        })