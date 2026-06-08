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

        feature = QgsFeature(paths.fields())
        feature.setGeometry(QgsGeometry.fromPolyline([QgsPoint(lon, lat) for lon, lat in points]))

        paths.startEditing()
        paths.addFeature(feature)
        paths.commitChanges()
