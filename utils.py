from typing import Optional

from qgis.core import (QgsFeature, QgsGeometry, QgsLayerTreeGroup, QgsPoint, QgsProject, QgsSymbol,
                       QgsVectorLayer, QgsWkbTypes, QgsTextBufferSettings, QgsTextFormat, QgsPalLayerSettings,
                       QgsVectorLayerSimpleLabeling, Qgis, QgsCoordinateReferenceSystem, QgsCoordinateTransform)
from qgis.PyQt.QtGui import QColor, QFont


class Utils:
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
    def create_directory() -> Optional[QgsLayerTreeGroup]:
        tracks = Utils.get_or_create_tracks_directory()

        if not tracks:
            return None

        root = QgsProject.instance().layerTreeRoot()
        route = root.addGroup(Utils.generate_name(tracks))
        clone = route.clone()
        tracks.insertChildNode(-1, clone)
        root.removeChildNode(route)

        return clone

    @staticmethod
    def create_polyline(points: list) -> QgsFeature:
        point_list = [
            QgsPoint(p[0], p[1]) for p in points
        ]

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolyline(point_list))

        return feature

    @staticmethod
    def create_polyline_geometry(points: list) -> QgsGeometry:
        point_list = [
            QgsPoint(p[0], p[1]) for p in points
        ]

        return QgsGeometry.fromPolyline(point_list)

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
    def refresh_position(layer: QgsVectorLayer):
        field_id = layer.fields().indexOf('position')

        for position, feature in enumerate(layer.getFeatures(), start=1):
            layer.changeAttributeValue(feature.id(), field_id, position)

    @staticmethod
    def transform_crs(geometry: QgsGeometry, src_crs_id: int, dst_crs_id: int) -> QgsGeometry:
        src_crs = QgsCoordinateReferenceSystem(src_crs_id)
        dst_crs = QgsCoordinateReferenceSystem(dst_crs_id)

        transform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())

        geometry.transform(transform)

        return geometry

    @staticmethod
    def set_data_source(layer: QgsVectorLayer, file_name: str):
        options = layer.dataProvider().ProviderOptions()
        options.driverName = 'GPX'

        layer.setDataSource(file_name, layer.name(), 'gpx', options)

    @staticmethod
    def set_symbol(layer: QgsVectorLayer, symbol: QgsSymbol):
        layer.startEditing()
        layer.renderer().setSymbol(symbol)
        layer.commitChanges()

    @staticmethod
    def generate_name(tracks: QgsLayerTreeGroup) -> str:
        return f'Track {len(tracks.children()) + 1}'

    @staticmethod
    def set_crs(layer: QgsVectorLayer, code: str):
        crs = layer.crs()
        crs.createFromString(code)

        layer.setCrs(crs)
