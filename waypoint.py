from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsPointXY, QgsVectorLayer

from .utils import Utils


class Waypoint:
    @staticmethod
    def create(layer: QgsVectorLayer, point: QgsPointXY):
        print(f'Waypoint::create({layer}, {point}')

        if not layer:
            return

        feature = QgsFeature(layer.fields())
        feature.setGeometry(QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())))

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()

    @staticmethod
    def move(layer: QgsVectorLayer, feature: int, position: int, point: QgsPointXY):
        print(f'Waypoint::move({layer}, {feature}, {position}, {point}')

        layer.startEditing()
        layer.changeGeometry(feature, QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())))
        layer.commitChanges()

    @staticmethod
    def delete(layer: QgsVectorLayer, point: QgsPointXY):
        print(f'Waypoint::delete({layer}, {point}')

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
