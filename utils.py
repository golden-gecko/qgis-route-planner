from qgis.core import (QgsFeature, QgsField, QgsGeometry, QgsLayerTreeGroup, QgsLineSymbol, QgsPoint, QgsProject,
                       QgsVectorLayer, QgsWkbTypes, QgsTextBufferSettings, QgsTextFormat, QgsPalLayerSettings,
                       QgsVectorLayerSimpleLabeling, Qgis)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor, QFont


class Utils:
    LAYER_NAME_POINT = 'Point'
    LAYER_NAME_PATH = 'Path'

    @staticmethod
    def get_or_create_point_layer(track) -> QgsVectorLayer | None:
        print('Utils::get_or_create_point_layer()')

        for child in track.children(): # TODO: Root has no children.
            if child.layer() and child.layer().name() == Utils.LAYER_NAME_POINT:
                return child.layer()

        layer = QgsVectorLayer('Point', Utils.LAYER_NAME_POINT, 'memory')
        layer.startEditing()
        layer.setLabelsEnabled(True)
        layer.setLabeling(Utils.create_label_settings())

        provider = layer.dataProvider()
        provider.addAttributes([QgsField('position', QVariant.Int)])

        layer.commitChanges()

        QgsProject.instance().addMapLayer(layer, False)

        node = track.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer

    @staticmethod
    def get_or_create_path_layer(track) -> QgsVectorLayer|None:
        print('Utils::get_or_create_path_layer()')

        for child in track.children(): # TODO: Root has no children.
            if child.layer() and child.layer().name() == Utils.LAYER_NAME_PATH:
                return child.layer()

        layer = QgsVectorLayer('LineString', Utils.LAYER_NAME_PATH, 'memory')

        QgsProject.instance().addMapLayer(layer, False)

        node = track.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer

    @staticmethod
    def get_parent_name(layer: QgsVectorLayer) -> str|None:
        tree_parent = Utils.get_parent(layer)

        if not tree_parent:
            return None

        return tree_parent.name()

    @staticmethod
    def get_parent(layer: QgsVectorLayer):
        tree_layer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())

        if not tree_layer:
            return None

        tree_parent = tree_layer.parent()

        if not tree_parent:
            return None

        return tree_parent

    @staticmethod
    def get_or_create_tracks_directory() -> QgsLayerTreeGroup:
        root = QgsProject.instance().layerTreeRoot()
        routes = root.findGroup('Tracks')

        if not routes:
            routes = root.addGroup('Tracks')
            clone = routes.clone()
            root.insertChildNode(0, clone)
            root.removeChildNode(routes)
            routes = clone

        return routes

    @staticmethod
    def create_directory(tracks: QgsLayerTreeGroup, name: str) -> QgsLayerTreeGroup:
        root = QgsProject.instance().layerTreeRoot()
        route = root.addGroup(name)
        clone = route.clone()
        tracks.insertChildNode(-1, clone)
        root.removeChildNode(route)

        return clone

    @staticmethod
    def create_point(point: QgsPoint, fields) -> QgsFeature:
        feature = QgsFeature(fields)
        feature.setGeometry(QgsGeometry.fromPoint(point))

        return feature

    @staticmethod
    def create_polyline(points: list) -> QgsFeature:
        point_list = [
            QgsPoint(p[0], p[1]) for p in points
        ]

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolyline(point_list))

        return feature

    @staticmethod
    def remove_non_point_geometries(layer: QgsVectorLayer, geometry_type):
        layer.startEditing()

        for feature in layer.getFeatures():
            if feature.geometry().type() != geometry_type:
                layer.deleteFeature(feature.id())

        layer.commitChanges()

    @staticmethod
    def update_layer(points_layer: QgsVectorLayer, path_layer: QgsVectorLayer, path: list):
        Utils.remove_non_point_geometries(points_layer, QgsWkbTypes.PointGeometry)

        vl = path_layer
        pr = vl.dataProvider()
        vl.startEditing()

        for feature in path_layer.getFeatures():
            path_layer.deleteFeature(feature.id())

        features = []

        for points in path:
            features.append(Utils.create_polyline(points))

        pr.addFeatures(features)
        vl.commitChanges()

    @staticmethod
    def create_label_settings() -> QgsVectorLayerSimpleLabeling:
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor('white'))

        text_format = QgsTextFormat()
        text_format.setFont(QFont('Arial', 12))
        text_format.setSize(12)
        text_format.setBuffer(buffer_settings)

        layer_settings = QgsPalLayerSettings()
        layer_settings.setFormat(text_format)
        layer_settings.fieldName = 'position'
        layer_settings.placement = Qgis.LabelPlacement.AroundPoint
        layer_settings.enabled = True

        return QgsVectorLayerSimpleLabeling(layer_settings)

    @staticmethod
    def get_point_count(layer: QgsVectorLayer) -> int:
        count = 0

        for feature in layer.getFeatures():
            if feature.geometry().type() == QgsWkbTypes.PointGeometry:
                count += 1

        return count

    @staticmethod
    def refresh_position(layer: QgsVectorLayer):
        field_id = layer.fields().indexOf('position')

        for position, feature in enumerate(layer.getFeatures(), start=1):
            layer.changeAttributeValue(feature.id(), field_id, position)
