from qgis.core import QgsFeature, QgsGeometry, QgsPoint


class Feature:
    @staticmethod
    def from_point(point: QgsPoint, fields) -> QgsFeature:
        feature = QgsFeature(fields)
        feature.setGeometry(QgsGeometry.fromPoint(point))

        return feature
