import xml.etree.ElementTree as ET

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
    def from_xml(waypoints: Optional[QgsLayerTreeGroup], wpt: ET.Element):
        if waypoints is None:
            return

        points = Layer.get_or_create_points(waypoints)

        if points is None:
            return

        wpt_name = wpt.find('name')

        if wpt_name is None:
            name = None
        else:
            name = wpt_name.text

        lon = wpt.get('lon')
        lat = wpt.get('lat')

        if lon is None or lat is None:
            return

        Waypoint.create(points, QgsPointXY(float(lon), float(lat)), name)

    @staticmethod
    @log_call
    def to_xml(waypoints: Optional[QgsLayerTreeGroup]) -> list[ET.Element]:
        if not waypoints:
            return []

        points = Layer.get_or_create_points(waypoints)

        if not points:
            return []

        wpts = []

        for feature in points.getFeatures():
            vertex = feature.geometry().asPoint()

            name = ET.Element('name')
            name.text = feature.attribute('name')

            wpt = ET.Element('wpt', lat=str(vertex.y()), lon=str(vertex.x()))
            wpt.append(name)

            wpts.append(wpt)

        return wpts
