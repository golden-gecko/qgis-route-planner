from typing import Optional

from qgis.core import (QgsFeature, QgsGeometry, QgsLayerTreeGroup, QgsPoint, QgsProject, QgsSymbol,
                       QgsVectorLayer,QgsTextBufferSettings, QgsTextFormat, QgsPalLayerSettings, QgsPointXY,
                       QgsVectorLayerSimpleLabeling, Qgis, QgsCoordinateReferenceSystem, QgsCoordinateTransform)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import QFileDialog


class Utils:
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
    def update_layer(points: QgsVectorLayer, paths: QgsVectorLayer, lines: list):
        print(f'Utils::update_layer({points}, {paths}, {lines})')

        # Utils.remove_non_point_geometries(points_layer, QgsWkbTypes.PointGeometry)

        provider = paths.dataProvider()
        paths.startEditing()

        for feature in paths.getFeatures():
            paths.deleteFeature(feature.id())

        features = []

        for vertices in lines:
            features.append(Utils.create_polyline(vertices))

        provider.addFeatures(features)
        paths.commitChanges()

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
        if not layer:
            return

        layer.startEditing()
        layer.renderer().setSymbol(symbol)
        layer.commitChanges()

    @staticmethod
    def generate_name(prefix: str, items: QgsLayerTreeGroup) -> str:
        return f'{prefix} {len(items.children()) + 1}'

    @staticmethod
    def set_crs(layer: QgsVectorLayer, code: str):
        crs = layer.crs()
        crs.createFromString(code)

        layer.setCrs(crs)

    @staticmethod
    def get_file_name_from_dialog() -> Optional[str]:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(['GPX files (*.gpx)'])

        if not dialog.exec_():
            return None

        if len(dialog.selectedFiles()) != 1:
            return None

        return dialog.selectedFiles()[0]

    @staticmethod
    def create_buffer(point: QgsPointXY, distance: float=0.001, segments: int=5):
        return QgsGeometry.fromPoint(QgsPoint(point.x(), point.y())).buffer(distance, segments)
