from qgis.core import QgsFeature, QgsPoint

from .utils import Utils


class Point:
    @staticmethod
    def create_start(layer, point):
        layer.startEditing()

        geometries = [
            Utils.create_point_geometry(QgsPoint(point.x(), point.y()))
        ]

        for feature in layer.getFeatures():
            geometries.append(feature.geometry())
            layer.deleteFeature(feature.id())

        for geometry in geometries:
            feature = QgsFeature(layer.fields())
            feature.setGeometry(geometry)

            layer.addFeature(feature)

        layer.commitChanges()

        layer.startEditing()
        Utils.refresh_position(layer)
        layer.commitChanges()

    @staticmethod
    def create_end(iface):
        pass

    @staticmethod
    def delete(iface):
        pass

    @staticmethod
    def move(iface):
        pass
