import gpxpy

from typing import Optional

from qgis.core import QgsFeature, QgsGeometry, QgsLayerTreeGroup, QgsPoint, QgsPointXY, QgsVectorLayer

from .layer import Layer
from .log import log_call
from .utils import Utils


class Waypoint:
    @staticmethod
    @log_call
    def create(layer: Optional[QgsVectorLayer], point: QgsPointXY, name: Optional[str] = None):
        if layer is None:
            return

        feature = QgsFeature(layer.fields())
        feature.setGeometry(QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())))

        if name:
            feature['name'] = name

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()

    @staticmethod
    @log_call
    def move(layer: Optional[QgsVectorLayer], feature: int, point: QgsPointXY):
        layer.startEditing()
        layer.changeGeometry(feature, QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())))
        layer.commitChanges()

    @staticmethod
    @log_call
    def delete(layer: Optional[QgsVectorLayer], point: QgsPointXY):
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

    @staticmethod
    @log_call
    def from_gpx(waypoints: Optional[QgsLayerTreeGroup], wpt: gpxpy.gpx.GPXWaypoint):
        """Import from a gpxpy waypoint object."""
        if waypoints is None:
            return

        points = Layer.get_or_create_points(waypoints)

        if points is None:
            return

        name = getattr(wpt, 'name', None)
        lat = getattr(wpt, 'latitude', None)
        lon = getattr(wpt, 'longitude', None)

        if lat is None or lon is None:
            return

        Waypoint.create(points, QgsPointXY(float(lon), float(lat)), name)

    @staticmethod
    @log_call
    def to_gpx_waypoints(waypoints: Optional[QgsLayerTreeGroup]) -> list[gpxpy.gpx.GPXWaypoint]:
        """Return a list of gpxpy GPXWaypoint objects for the given waypoints group."""
        if not waypoints:
            return []

        points = Layer.get_or_create_points(waypoints)

        if not points:
            return []

        wpts = []

        for feature in points.getFeatures():
            vertex = feature.geometry().asPoint()
            name = feature.attribute('name')
            wpt = gpxpy.gpx.GPXWaypoint(latitude=vertex.y(), longitude=vertex.x(), name=name)
            wpts.append(wpt)

        return wpts
