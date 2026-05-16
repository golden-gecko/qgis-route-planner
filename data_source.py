from qgis.core import QgsVectorLayer

from .log import log_call


class DataSource:
    @staticmethod
    @log_call
    def set_data_source(layer: QgsVectorLayer, file_name: str) -> None:
        data_provider = layer.dataProvider()

        if data_provider is None:
            return

        options = data_provider.ProviderOptions()
        options.driverName = 'GPX'

        layer.setDataSource(file_name, layer.name(), 'gpx', options)
