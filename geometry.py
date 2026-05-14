from qgis.core import QgsGeometry, QgsPoint


class Geometry:
    @staticmethod
    def from_point(point: QgsPoint) -> QgsGeometry:
        return QgsGeometry.fromPoint(point)