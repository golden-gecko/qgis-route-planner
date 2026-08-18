from qgis.core import QgsFeature, QgsGeometry, QgsPoint

from .geometry import Geometry


class Feature:
    @staticmethod
    def from_point(point: QgsPoint, fields) -> QgsFeature:
        feature = QgsFeature(fields)
        feature.setGeometry(QgsGeometry.fromPoint(point))

        return feature

    @staticmethod
    def from_points(points: list, fields) -> QgsFeature:
        feature = QgsFeature(fields)
        feature.setGeometry(Geometry.from_points(points))

        return feature
