from qgis.core import QgsFeature, QgsGeometry, QgsLayerTreeGroup, QgsPoint

from .tree import Tree


class Waypoint:
    @staticmethod
    def create(file: QgsLayerTreeGroup, lon: float, lat: float):
        waypoints = Tree.find_group(file, 'Waypoints')

        if not waypoints:
            return

        for child in waypoints.children():
            layer = child.layer()

            if not layer:
                continue

            layer.startEditing()

            feature = QgsFeature(layer.fields())
            feature.setGeometry(QgsGeometry.fromPoint(QgsPoint(lon, lat)))

            layer.addFeature(feature)
            layer.commitChanges()
