from qgis.core import QgsGeometry, QgsPoint, QgsWkbTypes
from qgis.gui import QgsMapTool
from qgis.PyQt.QtCore import Qt

from .point import Point
from .track import Track
from .utils import Utils


class PointCreateStart(QgsMapTool):
    def __init__(self, iface, canvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        track = Track.get_active(self.iface)
        layer = Utils.get_or_create_point_layer(track)
        point = self.toLayerCoordinates(layer, event.pos())

        Point.create_start(layer, point)
        Track.refresh_point_create_start(track, 1)


class PointCreateMiddle(QgsMapTool):
    def __init__(self, iface, canvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        track = Track.get_active(self.iface)
        layer = Utils.get_or_create_point_layer(track)
        point = self.toLayerCoordinates(layer, event.pos())
        buffer = QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(0.001,5)

        position = 1

        for feature in Utils.get_or_create_path_layer(track).getFeatures():
            print(f'feature {feature}')

            if feature.geometry().type() == QgsWkbTypes.LineGeometry:
                if feature.geometry().intersects(buffer):
                    # self.layer.getFeature(self.feature).attribute('position')

                    # for vertex in feature.geometry().vertices():
                    # print(f'  vertex {vertex}')

                    print(f'position: {position}')

                    Point.create_middle(layer, point, position + 1)
                    Track.refresh_point_create_middle(track, position + 1)

                    break

            position += 1


class PointCreateEnd(QgsMapTool):
    def __init__(self, iface, canvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        track = Track.get_active(self.iface)
        layer = Utils.get_or_create_point_layer(track)
        point = self.toLayerCoordinates(layer, event.pos())

        Point.create_end(layer, point)
        Track.refresh_point_create_end(track, layer.featureCount())


class PointMove(QgsMapTool):
    def __init__(self, iface, canvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.track = None
        self.layer = None
        self.feature = None

        self.setCursor(Qt.CrossCursor)

    def canvasPressEvent(self, event):
        self.track = Track.get_active(self.iface)
        self.layer = Utils.get_or_create_point_layer(self.track)

        point = self.toLayerCoordinates(self.layer, event.pos())
        buffer = QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(0.001,5)

        for feature in self.layer.getFeatures():
            if feature.geometry().type() == QgsWkbTypes.PointGeometry:
                if feature.geometry().intersects(buffer):
                    self.feature = feature.id()

                    break

    def canvasReleaseEvent(self, event):
        point = self.toLayerCoordinates(self.layer, event.pos())

        if self.feature:
            Point.move(self.layer, self.feature, point)
            Track.refresh_point_move(self.track, self.layer.getFeature(self.feature).attribute('position'))


class PointDelete(QgsMapTool):
    def __init__(self, iface, canvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        track = Track.get_active(self.iface)
        layer = Utils.get_or_create_point_layer(track)
        point = self.toLayerCoordinates(layer, event.pos())

        position = Point.delete(layer, point)

        if position is not None:
            Track.refresh_point_delete(track, position)
