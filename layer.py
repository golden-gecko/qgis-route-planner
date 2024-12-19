from typing import Optional

from qgis.core import QgsField, QgsLayerTreeGroup, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant

from .tree import Tree
from .utils import Utils


class Layer:
    @staticmethod
    def get_or_create_points(segment: QgsLayerTreeGroup) -> Optional[QgsVectorLayer]:
        print(f'Layer::get_or_create_points({segment})')

        points = Tree.find_layer(segment, 'Points')

        if points:
            return points.layer()

        layer = QgsVectorLayer('Point', 'Points', 'memory')
        layer.startEditing()
        layer.setLabelsEnabled(True)
        layer.setLabeling(Utils.create_label_settings())

        Utils.set_crs(layer, 'EPSG:4326')

        provider = layer.dataProvider()
        provider.addAttributes([QgsField('position', QVariant.Int)])

        layer.commitChanges()

        QgsProject.instance().addMapLayer(layer, False)

        node = segment.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer

    @staticmethod
    def get_or_create_paths(segment: QgsLayerTreeGroup) -> Optional[QgsVectorLayer]:
        print(f'Layer::get_or_create_paths({segment})')

        points = Tree.find_layer(segment, 'Paths')

        if points:
            return points.layer()

        layer = QgsVectorLayer('LineString', 'Paths', 'memory')
        layer.startEditing()
        layer.setLabelsEnabled(True)
        layer.setLabeling(Utils.create_label_settings())

        Utils.set_crs(layer, 'EPSG:4326')

        provider = layer.dataProvider()
        provider.addAttributes([QgsField('position', QVariant.Int)])

        layer.commitChanges()

        QgsProject.instance().addMapLayer(layer, False)

        node = segment.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer
