from qgis.core import Qgis, QgsPalLayerSettings, QgsTextBufferSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling
from qgis.PyQt.QtGui import QColor, QFont

from .log import log_call


class Label:
    @staticmethod
    @log_call
    def create_settings(field: str) -> QgsVectorLayerSimpleLabeling:
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor('white'))

        text_format = QgsTextFormat()
        text_format.setFont(QFont('Arial', 12))
        text_format.setSize(12)
        text_format.setBuffer(buffer_settings)

        layer_settings = QgsPalLayerSettings()
        layer_settings.setFormat(text_format)
        layer_settings.fieldName = field
        layer_settings.placement = Qgis.LabelPlacement.AroundPoint
        layer_settings.enabled = True

        return QgsVectorLayerSimpleLabeling(layer_settings)
