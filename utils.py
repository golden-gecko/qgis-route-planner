import re

from typing import Optional

from qgis.core import QgsFeature, QgsGeometry, QgsLayerTreeGroup, QgsPoint, QgsProject, QgsVectorLayer, QgsPointXY

from .feature import Feature
from .log import log_call


class Utils:
    @staticmethod
    @log_call
    def add_layer(parent: Optional[QgsLayerTreeGroup], layer: Optional[QgsVectorLayer]) -> None:
        if parent is None:
            return

        if layer is None:
            return

        QgsProject.instance().addMapLayer(layer, False)

        parent.addLayer(layer)

        node = QgsProject.instance().layerTreeRoot().findLayer(layer.id())

        if node is None:
            return

        node.setItemVisibilityChecked(False)

    @staticmethod
    @log_call
    def update_layer(paths: QgsVectorLayer, lines: list):
        provider = paths.dataProvider()
        paths.startEditing()

        for feature in paths.getFeatures():
            paths.deleteFeature(feature.id())

        features = []

        for vertices in lines:
            features.append(Feature.from_points(vertices, paths.fields()))

        provider.addFeatures(features)
        paths.commitChanges()

    @staticmethod
    def refresh_position(layer: Optional[QgsVectorLayer]):
        field_id = layer.fields().indexOf('position')

        for position, feature in enumerate(layer.getFeatures(), start=1):
            layer.changeAttributeValue(feature.id(), field_id, position)

    @staticmethod
    def create_buffer(point: QgsPointXY, distance: float = 0.001, segments: int = 5):
        return QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(distance, segments)

    @staticmethod
    def update_distance(group: Optional[QgsLayerTreeGroup], distance: float) -> None:
        if group is None:
            return

        name = group.name()
        name = re.sub(r'\s*\[\d+(?:\.\d+)?\s+km\]\s*$', '', name)
        name = name.strip()

        group.setName(f'{name} [{distance:.2f} km]')
