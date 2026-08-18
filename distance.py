import math

from geographiclib.geodesic import Geodesic

from qgis.core import QgsDistanceArea


class Distance:
    @staticmethod
    def get_between_points(a: tuple[float, float], b: tuple[float, float]) -> float:
        result = Geodesic.WGS84.Inverse(a[1], a[0], b[1], b[0])

        return float(result['s12'])

    @staticmethod
    def get(paths) -> float:
        d = QgsDistanceArea()
        d.setEllipsoid('WGS84')

        return sum([d.measureLength(feature.geometry()) for feature in paths.getFeatures()]) / 1000.0

    @staticmethod
    def turn_delta_deg(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
        v1x = b[0] - a[0]
        v1y = b[1] - a[1]
        v2x = c[0] - b[0]
        v2y = c[1] - b[1]

        if (v1x == 0.0 and v1y == 0.0) or (v2x == 0.0 and v2y == 0.0):
            return 0.0

        angle1 = math.atan2(v1y, v1x)
        angle2 = math.atan2(v2y, v2x)

        delta = abs(math.degrees(angle2 - angle1))

        if delta > 180.0:
            delta = 360.0 - delta

        return delta
