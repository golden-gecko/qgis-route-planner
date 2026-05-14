from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsPointXY, QgsVectorLayer

from .feature import Feature
from .log import log_call
from .geometry import Geometry
from .utils import Utils


class Point:
    @staticmethod
    def create_geometry(point: QgsPoint) -> QgsGeometry:
        return QgsGeometry.fromPoint(point)

    @staticmethod
    @log_call
    def create_start(layer: QgsVectorLayer, point: QgsPointXY):

        layer.startEditing()

        geometries = [
            Geometry.from_point(QgsPoint(point.x(), point.y()))
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
    @log_call
    def create_middle(layer: QgsVectorLayer, point: QgsPointXY, position: int):

        layer.startEditing()

        geometries = []

        for local_position, feature in enumerate(layer.getFeatures(), start=1):
            if local_position == position:
                geometries.append(Geometry.from_point(QgsPoint(point.x(), point.y())))

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
    @log_call
    def create_end(layer: QgsVectorLayer, point: QgsPointXY):

        feature = Feature.from_point(QgsPoint(point.x(), point.y()), layer.fields())

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()

        layer.startEditing()
        Utils.refresh_position(layer)
        layer.commitChanges()

    @staticmethod
    @log_call
    def move(layer: QgsVectorLayer, feature: int, position: int, point: QgsPointXY):

        layer.startEditing()
        layer.changeGeometry(feature, QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())))
        layer.commitChanges()

    @staticmethod
    @log_call
    def delete(layer: QgsVectorLayer, point: QgsPointXY):

        buffer = Utils.create_buffer(point)

        for position, feature in enumerate(layer.getFeatures(), start=1):
            if feature.geometry().intersects(buffer):
                layer.startEditing()
                layer.deleteFeature(feature.id())
                layer.commitChanges()

                layer.startEditing()
                Utils.refresh_position(layer)
                layer.commitChanges()

                return position

        return None