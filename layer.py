from typing import Optional

from qgis.core import QgsField, QgsLayerTreeGroup, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant

from .crs import Crs
from .label import Label
from .log import log_call
from .tree import Tree


class Layer:
    @staticmethod
    @log_call
    def get_or_create_waypoints(segment: Optional[QgsLayerTreeGroup]) -> Optional[QgsVectorLayer]:
        points = Tree.find_layer(segment, 'Points')

        if points:
            return points.layer()

        layer = QgsVectorLayer('Point', 'Points', 'memory')
        layer.startEditing()
        layer.setLabelsEnabled(True)
        layer.setLabeling(Label.create_settings('name'))

        Crs.set(layer, 'EPSG:4326')

        provider = layer.dataProvider()
        provider.addAttributes([QgsField('name', QVariant.String)])

        layer.commitChanges()

        QgsProject.instance().addMapLayer(layer, False)

        node = segment.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer

    @staticmethod
    @log_call
    def get_or_create_points(segment: Optional[QgsLayerTreeGroup]) -> Optional[QgsVectorLayer]:
        if segment is None:
            return None

        points = Tree.find_layer(segment, 'Points')

        if points:
            return points.layer()

        layer = QgsVectorLayer('Point', 'Points', 'memory')
        layer.startEditing()
        layer.setLabelsEnabled(True)
        layer.setLabeling(Label.create_settings('position'))

        Crs.set(layer, 'EPSG:4326')

        provider = layer.dataProvider()
        provider.addAttributes([QgsField('position', QVariant.Int)])

        layer.commitChanges()

        QgsProject.instance().addMapLayer(layer, False)

        node = segment.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer

    @staticmethod
    @log_call
    def get_or_create_paths(segment: Optional[QgsLayerTreeGroup]) -> Optional[QgsVectorLayer]:
        if segment is None:
            return None

        points = Tree.find_layer(segment, 'Paths')

        if points:
            return points.layer()

        layer = QgsVectorLayer('LineString', 'Paths', 'memory')
        layer.startEditing()

        Crs.set(layer, 'EPSG:4326')

        provider = layer.dataProvider()
        provider.addAttributes([QgsField('position', QVariant.Int)])

        layer.commitChanges()

        QgsProject.instance().addMapLayer(layer, False)

        node = segment.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer
