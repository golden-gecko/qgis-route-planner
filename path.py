from typing import Optional

from qgis.core import QgsFeature, QgsGeometry, QgsLayerTreeGroup, QgsPoint

from .tree import Tree


class Path:
    @staticmethod
    def create(segment: Optional[QgsLayerTreeGroup], points: list):
        if segment is None:
            return

        paths = Tree.find_layer(segment, 'Paths')

        if paths is None:
            return

        layer = paths.layer()

        if layer is None:
            return

        feature = QgsFeature(layer.fields())
        feature.setGeometry(QgsGeometry.fromPolyline([QgsPoint(lon, lat) for lon, lat in points]))

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()
