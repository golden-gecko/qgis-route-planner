from qgis.core import QgsGeometry, QgsPoint, QgsVectorLayer, QgsWkbTypes
from qgis.gui import QgsMapTool
from qgis.PyQt.QtCore import Qt

from .utils import Utils


class PointAdd(QgsMapTool):
    def __init__(self, canvas, layer: QgsVectorLayer):
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.layer = layer

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        point = self.toLayerCoordinates(self.layer, event.pos())

        self.layer.startEditing()
        self.layer.addFeature(Utils.create_point(QgsPoint(point.x(), point.y())))
        self.layer.commitChanges()


class PointDelete(QgsMapTool):
    def __init__(self, canvas, layer: QgsVectorLayer):
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.layer = layer

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        point = self.toLayerCoordinates(self.layer, event.pos())
        buffer = QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(0.001,5)

        for feature in self.layer.getFeatures():
            if feature.geometry().type() == QgsWkbTypes.PointGeometry:
                if feature.geometry().intersects(buffer):
                    self.layer.startEditing()
                    self.layer.deleteFeature(feature.id())
                    self.layer.commitChanges()

                    break


class PointMove(QgsMapTool):
    def __init__(self, canvas, layer: QgsVectorLayer):
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.layer = layer
        self.feature = None

        self.setCursor(Qt.CrossCursor)

    def canvasPressEvent(self, event):
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

"""
class TrackEditTool(QgsMapTool):
    def __init__(self, canvas, track: QgsLayerTreeGroup):
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.track = track

        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        path_layer = Utils.get_or_create_path_layer(self.track)

        if not path_layer:
            return

        point = self.toLayerCoordinates(path_layer, event.pos())
        geometry = QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(10000,5)

        feature = QgsFeature()
        feature.setGeometry(geometry)

        path_layer.startEditing()
        path_layer.addFeature(feature)
        path_layer.commitChanges()

        areas = []
        for line_feature in line_layer.getFeatures():
            cands = area_layer.getFeatures(QgsFeatureRequest().setFilterRect(line_feature.geometry().boundingBox()))

            for area_feature in cands:
                if line_feature.geometry().intersects(area_feature.geometry()):
                    areas.append(area_feature.id())

        area_layer.select(areas)

        print(point)
"""
