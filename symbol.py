from typing import Optional

from qgis.core import QgsLineSymbol, QgsMarkerSymbol, QgsSymbol, QgsVectorLayer
from qgis.PyQt.QtGui import QColor


class Symbol:
    @staticmethod
    def create_point(color: QColor) -> Optional[QgsSymbol]:
        return QgsMarkerSymbol.createSimple({
            'color': color,
            'outline_color': color,
            'size': 3,
        })

    @staticmethod
    def create_path(color: QColor) -> Optional[QgsSymbol]:
        return QgsLineSymbol.createSimple({
            'color': color,
            'line_style': 'dash',
            'width': 0.75,
        })

    @staticmethod
    def create_waypoint(color: QColor) -> Optional[QgsSymbol]:
        return QgsMarkerSymbol.createSimple({
            'color': color,
            'outline_color': 'black',
            'size': 3,
        })

    @staticmethod
    def set(layer: QgsVectorLayer, symbol: Optional[QgsSymbol]):
        if layer is None:
            return

        if symbol is None:
            return

        renderer = layer.renderer()

        if renderer is None:
            return

        layer.startEditing()
        renderer.setSymbol(symbol)
        layer.commitChanges()
