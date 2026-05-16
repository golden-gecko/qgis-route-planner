from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsVectorLayer, QgsPointXY

from .log import log_call


class Utils:
    @staticmethod
    def create_polyline(points: list, fields) -> QgsFeature:
        point_list = [
            QgsPoint(p[0], p[1]) for p in points
        ]

        feature = QgsFeature(fields)
        feature.setGeometry(QgsGeometry.fromPolyline(point_list))

        return feature

    @staticmethod
    def create_polyline_geometry(points: list) -> QgsGeometry:
        point_list = [
            QgsPoint(p[0], p[1]) for p in points
        ]

        return QgsGeometry.fromPolyline(point_list)

    @staticmethod
    @log_call
    def update_layer(paths: QgsVectorLayer, lines: list):
        provider = paths.dataProvider()
        paths.startEditing()

        for feature in paths.getFeatures():
            paths.deleteFeature(feature.id())

        features = []

        for vertices in lines:
            features.append(Utils.create_polyline(vertices, paths.fields()))

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
