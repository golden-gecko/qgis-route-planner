from qgis.core import QgsGeometry, QgsPoint, QgsVectorLayer, QgsWkbTypes
from qgis.gui import QgsMapTool
from qgis.PyQt.QtCore import Qt

from .track import Track
from .utils import Utils


class PointAdd(QgsMapTool):
    def __init__(self, iface, canvas):
        QgsMapTool.__init__(self, canvas)

        self.iface = iface
        self.canvas = canvas

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        track = Track.get_active(self.iface)
        layer = Utils.get_or_create_point_layer(track)
        point = self.toLayerCoordinates(layer, event.pos())

        feature = Utils.create_point(QgsPoint(point.x(), point.y()), layer.fields())

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()

        layer.startEditing()
        Utils.refresh_position(layer)
        layer.commitChanges()

        Track.refresh(track)


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
        buffer = QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(0.001,5)

        for feature in layer.getFeatures():
            if feature.geometry().type() == QgsWkbTypes.PointGeometry:
                if feature.geometry().intersects(buffer):
                    layer.startEditing()
                    layer.deleteFeature(feature.id())
                    layer.commitChanges()

                    layer.startEditing()
                    Utils.refresh_position(layer)
                    layer.commitChanges()

                    Track.refresh(track)

                    break


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
            self.layer.startEditing()
            self.layer.changeGeometry(self.feature, QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())))
            self.layer.commitChanges()

            Track.refresh(self.track)
