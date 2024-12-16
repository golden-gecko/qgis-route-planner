from qgis.core import QgsGeometry, QgsPoint, QgsWkbTypes
from qgis.gui import QgsMapCanvas, QgsMapTool
from qgis.PyQt.QtCore import Qt

from .point import Point
from .segment import Segment
from .track import Track


class PointCreateStart(QgsMapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        segment = Segment.get_active(self.iface)

        if not segment:
            return

        point = self.toLayerCoordinates(segment.layer(), event.pos())

        Point.create_start(segment.layer(), point)
        # Track.refresh_point_create_start(track, 1)


class PointCreateMiddle(QgsMapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        track = Track.get_active(self.iface)
        layer = Track.get_or_create_point_layer(track)
        point = self.toLayerCoordinates(layer, event.pos())
        buffer = QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(0.001,5)

        position = 1

        for feature in Track.get_or_create_path_layer(track).getFeatures():
            if feature.geometry().type() == QgsWkbTypes.LineGeometry:
                if feature.geometry().intersects(buffer):
                    Point.create_middle(layer, point, position + 1)
                    Track.refresh_point_create_middle(track, position + 1)

                    break

            position += 1


class PointCreateEnd(QgsMapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        track = Track.get_active(self.iface)

        if not track:
            return

        layer = Track.get_or_create_point_layer(track)

        if not layer:
            return

        point = self.toLayerCoordinates(layer, event.pos())

        Point.create_end(layer, point)
        Track.refresh_point_create_end(track, layer.featureCount())


class PointMove(QgsMapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.track = None
        self.layer = None
        self.feature = None
        self.local_position = 0

        self.setCursor(Qt.CrossCursor)

    def canvasPressEvent(self, event):
        self.track = Track.get_active(self.iface)

        if not self.track:
            return

        self.layer = Track.get_or_create_point_layer(self.track)

        if not self.layer:
            return

        point = self.toLayerCoordinates(self.layer, event.pos())
        buffer = QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(0.001,5)

        for local_position, feature in enumerate(self.layer.getFeatures(), start=1):
            if feature.geometry().type() == QgsWkbTypes.PointGeometry:
                if feature.geometry().intersects(buffer):
                    self.local_position = local_position
                    self.feature = feature.id()

                    break

    def canvasReleaseEvent(self, event):
        point = self.toLayerCoordinates(self.layer, event.pos())

        if self.feature:
            Point.move(self.layer, self.feature, self.local_position, point)
            Track.refresh_point_move(self.track, self.local_position)


class PointDelete(QgsMapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        track = Track.get_active(self.iface)

        if not track:
            return

        layer = Track.get_or_create_point_layer(track)

        if not layer:
            return

        point = self.toLayerCoordinates(layer, event.pos())

        position = Point.delete(layer, point)

        if position is not None:
            Track.refresh_point_delete(track, position)
