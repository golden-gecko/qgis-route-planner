from qgis.core import QgsWkbTypes
from qgis.gui import QgsMapCanvas, QgsMapTool
from qgis.PyQt.QtCore import Qt

from .layer import Layer
from .point import Point
from .segment import Segment
from .track import Track
from .utils import Utils


class MapTool(QgsMapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)


class PointCreateStart(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

    def canvasReleaseEvent(self, event):
        print('PointCreateStart::canvasReleaseEvent()')

        segment = Segment.get_active(self.iface)

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())

        Point.create_start(points, point)
        Segment.refresh_point(segment, 1)


class PointCreateMiddle(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

    def canvasReleaseEvent(self, event):
        print('PointCreateMiddle::canvasReleaseEvent()')

        segment = Segment.get_active(self.iface)

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return

        point = self.toLayerCoordinates(points, event.pos())
        buffer = Utils.create_buffer(point)

        for position, feature in enumerate(paths.getFeatures(), start=1):
            if not feature.geometry().intersects(buffer):
                continue

            Point.create_middle(points, point, position + 1)
            Segment.refresh_point(segment, position + 1)

            break


class PointCreateEnd(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

    def canvasReleaseEvent(self, event):
        print('PointCreateEnd::canvasReleaseEvent()')

        track = Track.get_active(self.iface)

        if not track:
            return

        segment = Segment.get_active(self.iface)

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())

        Point.create_end(points, point)
        Segment.refresh_point(segment, points.featureCount())


class PointMove(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

        self.feature = None
        self.feature_position = None

    def canvasPressEvent(self, event):
        print('PointMove::canvasPressEvent()')

        segment = Segment.get_active(self.iface)

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())
        buffer = Utils.create_buffer(point)

        for feature_position, feature in enumerate(points.getFeatures(), start=1):
            if feature.geometry().intersects(buffer):
                self.feature = feature.id()
                self.feature_position = feature_position

                break

    def canvasReleaseEvent(self, event):
        print('PointMove::canvasReleaseEvent()')

        segment = Segment.get_active(self.iface)

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())

        if self.feature:
            Point.move(points, self.feature, self.feature_position, point)
            Segment.refresh_point_move(segment, self.feature_position)


class PointDelete(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

    def canvasReleaseEvent(self, event):
        print('PointDelete::canvasReleaseEvent()')

        segment = Segment.get_active(self.iface)

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())
        position = Point.delete(points, point)

        if position is not None:
            Segment.refresh_point_delete(segment, position)
