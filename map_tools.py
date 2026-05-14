from qgis.gui import QgsMapCanvas, QgsMapTool
from qgis.PyQt.QtCore import Qt

from .file import File
from .log import log_call
from .layer import Layer
from .point import Point
from .segment import Segment
from .track import Track
from .tree import Tree
from .utils import Utils
from .waypoint import Waypoint


class MapTool(QgsMapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)


class Edit(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

        self.feature = None
        self.feature_position = None
        self.feature_type = None

    @log_call
    def canvasMoveEvent(self, event):
        pass

    @log_call
    def canvasPressEvent(self, event):

        if event.button() != Qt.LeftButton:
            return

        self.feature = None
        self.feature_position = None
        self.feature_type = None

        segment = Segment.get_active(self.iface)

        if not segment:
            return

        # check if user is selecting a point
        points = Layer.get_or_create_points(segment)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())
        buffer = Utils.create_buffer(point)

        for feature_position, feature in enumerate(points.getFeatures(), start=1):
            if feature.geometry().intersects(buffer):
                self.feature = feature.id()
                self.feature_position = feature_position
                self.feature_type = 'point'
                File.refresh_distance(File.get_active(self.iface))

                return

        # check if user is selecting a path
        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return

        point = self.toLayerCoordinates(paths, event.pos())
        buffer = Utils.create_buffer(point)

        for feature_position, feature in enumerate(paths.getFeatures(), start=1):
            if feature.geometry().intersects(buffer):
                self.feature = feature.id()
                self.feature_position = feature_position
                self.feature_type = 'path'

                return

    @log_call
    def canvasReleaseEvent(self, event):

        segment = Segment.get_active(self.iface)

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())

        if self.feature and self.feature_position:
            if self.feature_type == 'point':
                if event.button() == Qt.LeftButton:
                    Point.move(points, self.feature, self.feature_position, point)
                    Segment.refresh_point_move(segment, self.feature_position)
                elif event.button() == Qt.RightButton:
                    position = Point.delete(points, point)

                    if position is not None:
                        Segment.refresh_point_delete(segment, position)
            elif self.feature_type == 'path':
                if event.button() == Qt.LeftButton:
                    Point.create_middle(points, point, self.feature_position + 1)
                    Segment.refresh_point(segment, self.feature_position + 1)

class WaypointCreate(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

    @log_call
    def canvasReleaseEvent(self, event):

        file = File.get_active(self.iface)

        if not file:
            return

        waypoints = Tree.find_group(file, 'Waypoints')

        if not waypoints:
            return

        points = Layer.get_or_create_points(waypoints)

        if not points:
            return

        Waypoint.create(points, self.toLayerCoordinates(points, event.pos()), Utils.generate_name('Waypoint', points.featureCount()))


class WaypointDelete(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

    @log_call
    def canvasReleaseEvent(self, event):

        file = File.get_active(self.iface)

        if not file:
            return

        waypoints = Tree.find_group(file, 'Waypoints')

        if not waypoints:
            return

        points = Layer.get_or_create_points(waypoints)

        if not points:
            return

        Waypoint.delete(points, self.toLayerCoordinates(points, event.pos()))


class WaypointMove(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

        self.feature = None
        self.feature_position = None

    @log_call
    def canvasPressEvent(self, event):

        self.feature = None
        self.feature_position = None

        file = File.get_active(self.iface)

        if not file:
            return

        waypoints = Tree.find_group(file, 'Waypoints')

        if not waypoints:
            return

        points = Layer.get_or_create_points(waypoints)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())
        buffer = Utils.create_buffer(point)

        for feature_position, feature in enumerate(points.getFeatures(), start=1):
            if feature.geometry().intersects(buffer):
                self.feature = feature.id()
                self.feature_position = feature_position

                break

    @log_call
    def canvasReleaseEvent(self, event):

        file = File.get_active(self.iface)

        if not file:
            return

        waypoints = Tree.find_group(file, 'Waypoints')

        if not waypoints:
            return

        points = Layer.get_or_create_points(waypoints)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())

        if self.feature and self.feature_position:
            Waypoint.move(points, self.feature, self.feature_position, point)


class PointCreateStart(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

    @log_call
    def canvasReleaseEvent(self, event):

        segment = Segment.get_active(self.iface)

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())

        Point.create_start(points, point)
        Segment.refresh_point(segment, 1)
        File.refresh_distance(File.get_active(self.iface))


class PointCreateMiddle(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

    @log_call
    def canvasReleaseEvent(self, event):

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
            if feature.geometry().intersects(buffer):
                Point.create_middle(points, point, position + 1)
                Segment.refresh_point(segment, position + 1)
                File.refresh_distance(File.get_active(self.iface))

                break


class PointCreateEnd(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

    @log_call
    def canvasReleaseEvent(self, event):

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
        File.refresh_distance(File.get_active(self.iface))


class PointMove(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

        self.feature = None
        self.feature_position = None

    @log_call
    def canvasPressEvent(self, event):

        self.feature = None
        self.feature_position = None

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
                File.refresh_distance(File.get_active(self.iface))

                break

    @log_call
    def canvasReleaseEvent(self, event):

        segment = Segment.get_active(self.iface)

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        point = self.toLayerCoordinates(points, event.pos())

        if self.feature and self.feature_position:
            Point.move(points, self.feature, self.feature_position, point)
            Segment.refresh_point_move(segment, self.feature_position)
            File.refresh_distance(File.get_active(self.iface))


class PointDelete(MapTool):
    def __init__(self, iface, canvas: QgsMapCanvas):
        MapTool.__init__(self, iface, canvas)

    @log_call
    def canvasReleaseEvent(self, event):

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
            File.refresh_distance(File.get_active(self.iface))
