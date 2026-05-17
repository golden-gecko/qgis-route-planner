import math

from geographiclib.geodesic import Geodesic
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

    @staticmethod
    def turn_delta_deg(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
        v1x = b[0] - a[0]
        v1y = b[1] - a[1]
        v2x = c[0] - b[0]
        v2y = c[1] - b[1]

        if (v1x == 0 and v1y == 0) or (v2x == 0 and v2y == 0):
            return 0.0

        angle1 = math.atan2(v1y, v1x)
        angle2 = math.atan2(v2y, v2x)
        delta = abs(math.degrees(angle2 - angle1))

        if delta > 180.0:
            delta = 360.0 - delta

        return delta

    @staticmethod
    def distance_m(a: tuple[float, float], b: tuple[float, float]) -> float:
        result = Geodesic.WGS84.Inverse(a[1], a[0], b[1], b[0])
        return float(result['s12'])
