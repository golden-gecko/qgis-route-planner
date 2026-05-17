from qgis.core import QgsGeometry, QgsPoint


class Geometry:
    @staticmethod
    def from_point(point: QgsPoint) -> QgsGeometry:
        return QgsGeometry.fromPoint(point)

    @staticmethod
    def from_points(points: list) -> QgsGeometry:
        point_list = [
            QgsPoint(p[0], p[1]) for p in points
        ]

        return QgsGeometry.fromPolyline(point_list)
