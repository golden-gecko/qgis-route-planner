from qgis.core import QgsGeometry, QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsCoordinateTransform


class Crs:
    @staticmethod
    def set(layer: QgsVectorLayer, code: str) -> None:
        crs = layer.crs()
        crs.createFromString(code)

        layer.setCrs(crs)

    @staticmethod
    def transform(geometry: QgsGeometry, src_crs_id: int, dst_crs_id: int) -> QgsGeometry:
        src_crs = QgsCoordinateReferenceSystem(src_crs_id)
        dst_crs = QgsCoordinateReferenceSystem(dst_crs_id)

        transform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())

        geometry.transform(transform)

        return geometry
