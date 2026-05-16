from qgis.core import QgsDistanceArea


class Distance:
    @staticmethod
    def get(paths) -> float:
        d = QgsDistanceArea()
        d.setEllipsoid('WGS84')

        return sum([d.measureLength(feature.geometry()) for feature in paths.getFeatures()]) / 1000.0
