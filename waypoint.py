import xml.etree.ElementTree as ET

from qgis.core import QgsFeature, QgsGeometry, QgsLayerTreeGroup, QgsPoint, QgsPointXY, QgsVectorLayer

from .layer import Layer
from .log import log_call
from .utils import Utils


class Waypoint:
    @staticmethod
    @log_call
    def create(layer: QgsVectorLayer, point: QgsPointXY, name: str = None):

        if not layer:
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

    @staticmethod
    @log_call
    def from_xml(waypoints: QgsLayerTreeGroup, wpt: ET.Element):

        if not waypoints:
            return

        points = Layer.get_or_create_points(waypoints)

        if not points:
            return

        wpt_name = wpt.find('name')

        if wpt_name is not None:
            name = wpt_name.text
        else:
            name = None

        Waypoint.create(points, QgsPointXY(float(wpt.get('lon')), float(wpt.get('lat'))), name)

    @staticmethod
    @log_call
    def to_xml(waypoints: QgsLayerTreeGroup) -> list[ET.Element]:

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
