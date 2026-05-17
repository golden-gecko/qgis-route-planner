from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsVectorLayer, QgsPointXY

from .feature import Feature
from .geometry import Geometry
from .log import log_call


class Utils:
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
    def refresh_position(layer: QgsVectorLayer):
        field_id = layer.fields().indexOf('position')

        for position, feature in enumerate(layer.getFeatures(), start=1):
            layer.changeAttributeValue(feature.id(), field_id, position)

    @staticmethod
    def create_buffer(point: QgsPointXY, distance: float = 0.001, segments: int = 5):
        return QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(distance, segments)
