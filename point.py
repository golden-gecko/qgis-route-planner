from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsWkbTypes

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
    def create_middle(layer, point, position: int):
        layer.startEditing()

        geometries = []

        for feature in layer.getFeatures():
            local_position = feature.attribute('position')

            if local_position == position:
                geometries.append(Utils.create_point_geometry(QgsPoint(point.x(), point.y())))

            print(f'local_position: {local_position}, position: {position}')

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
    def create_end(layer, point):
        feature = Utils.create_point(QgsPoint(point.x(), point.y()), layer.fields())

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()

        layer.startEditing()
        Utils.refresh_position(layer)
        layer.commitChanges()

    @staticmethod
    def delete(layer, point):
        buffer = QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(0.001,5)

        for feature in layer.getFeatures():
            if feature.geometry().type() == QgsWkbTypes.PointGeometry:
                if feature.geometry().intersects(buffer):
                    position = feature.attribute('position')

                    layer.startEditing()
                    layer.deleteFeature(feature.id())
                    layer.commitChanges()

                    layer.startEditing()
                    Utils.refresh_position(layer)
                    layer.commitChanges()

                    return position

        return None

    @staticmethod
    def move(layer, feature, point):
        layer.startEditing()
        layer.changeGeometry(feature, QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())))
        layer.commitChanges()
