from qgis.core import QgsFeature, QgsGeometry, QgsLayerTreeGroup, QgsPoint

from .tree import Tree


class Path:
    @staticmethod
    def create(segment: QgsLayerTreeGroup, points: list):
        paths = Tree.find_layer(segment, 'Paths')

        if not paths:
            return

        layer = paths.layer()

        if not layer:
            return

        feature = QgsFeature(layer.fields())
        feature.setGeometry(QgsGeometry.fromPolyline([QgsPoint(lon, lat) for lon, lat in points]))

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()