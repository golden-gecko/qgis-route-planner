import copy
import pathlib
import re

from typing import Optional

from qgis.core import QgsFillSymbol, QgsLayerTreeGroup, QgsLineSymbol, QgsMarkerSymbol, QgsProject, QgsRasterLayer, QgsSingleSymbolRenderer, QgsVectorLayer
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor

from .config import Config
from .log import log_call
from .utils import Utils


class Tree:
    @staticmethod
    @log_call
    def get_root(name: str = 'RoutePlanner') -> Optional[QgsLayerTreeGroup]:
        instance = QgsProject.instance()

        if instance is None:
            return None

        root = instance.layerTreeRoot()

        if root is None:
            return None

        files = root.findGroup(name)

        if files is not None:
            return files

        return Tree.create_group(root, name, None, 0)

    @staticmethod
    @log_call
    def process_group(parent: Optional[QgsLayerTreeGroup], item: dict) -> Optional[QgsLayerTreeGroup]:
        if parent is None:
            return None

        if 'name' not in item:
            return None

        group = Tree.get_or_create_group(parent, item['name'])

        if group is None:
            return None

        for child in item.get('items', []):
            Tree.process_item(group, child)

        return group

    @staticmethod
    @log_call
    def process_raster(parent: Optional[QgsLayerTreeGroup], item: dict) -> None:
        if parent is None:
            return

        if 'uri' not in item:
            return

        if 'name' in item:
            name = item['name']
        else:
            name = pathlib.Path(item['uri']).stem

        layer = Tree.find_layer(parent, name)

        if layer is not None:
            return

        layer = Tree.make_raster(item['uri'], name)

        if not layer.isValid():
            return

        Utils.add_layer(parent, layer)

    @staticmethod
    @log_call
    def process_item(parent: Optional[QgsLayerTreeGroup], item: dict) -> None:
        if 'type' not in item:
            return

        if item['type'] == 'group':
            Tree.process_group(parent, item)
        elif item['type'] == 'raster':
            Tree.process_raster(parent, item)
        elif item['type'] == 'vector':
            Tree.process_vector(parent, item)

    @staticmethod
    @log_call
    def create_tree_structure() -> None:
        root = Tree.get_root()

        if root is None:
            return

        for item in Config.Tree.Items:
            Tree.process_item(root, item)

    @staticmethod
    @log_call
    def get_or_create_group(parent: Optional[QgsLayerTreeGroup], name: str) -> Optional[QgsLayerTreeGroup]:
        if parent is None:
            return None

        group = Tree.find_group(parent, name)

        if group is not None:
            return group

        return Tree.create_group(parent, name)

    @staticmethod
    @log_call
    def create_group(parent: Optional[QgsLayerTreeGroup], name: str, custom_type: Optional[str] = None, position: int = -1) -> Optional[QgsLayerTreeGroup]:
        if parent is None:
            return None

        group = parent.addGroup(name)

        if group is None:
            return None

        group_clone = group.clone()

        if group_clone is None:
            return None

        if custom_type:
            group_clone.setCustomProperty('type', custom_type)

        parent.insertChildNode(position, group_clone)
        parent.removeChildNode(group)

        return group_clone

    @staticmethod
    @log_call
    def find_group(parent: Optional[QgsLayerTreeGroup], name: str) -> Optional[QgsLayerTreeGroup]:
        if parent is None:
            return None

        return parent.findGroup(name)

    @staticmethod
    @log_call
    def find_layer_by_path(path: str) -> Optional[QgsVectorLayer]:
        root = Tree.get_root()

        if root is None:
            return None

        parts = path.split('.')
        parent = root

        for part in parts[:-1]:
            parent = Tree.find_group(parent, part)

            if parent is None:
                return None

        return Tree.find_layer(parent, parts[-1])

    @staticmethod
    @log_call
    def find_layer(parent: Optional[QgsLayerTreeGroup], name: str) -> Optional[QgsVectorLayer]:
        if parent is None:
            return None

        for child in parent.children():
            if child.name() == name:
                return child.layer()

        return None

    @staticmethod
    @log_call
    def delete_group(group: Optional[QgsLayerTreeGroup]) -> None:
        if group is None:
            return

        parent = group.parent()

        if parent is not None:
            parent.removeChildNode(group)

    @staticmethod
    @log_call
    def process_vector(parent: Optional[QgsLayerTreeGroup], item: dict) -> None:
        if parent is None:
            return

        if 'uri' not in item:
            return

        if 'path' in item and 'pattern' in item:
            for path_item in pathlib.Path(item['path']).glob('*'):
                if path_item.is_dir():
                    new_item = {
                        'type': 'group',
                        'name': path_item.stem,
                    }

                    if Config.Tree.RefreshDirectory == False and Tree.find_group(parent, new_item['name']) is not None:
                        continue

                    group = Tree.process_group(parent, new_item)

                    if group is None:
                        continue

                    new_item = copy.deepcopy(item)
                    new_item['path'] = str(path_item.resolve())

                    Tree.process_vector(group, new_item)

            for path_item in pathlib.Path(item['path']).glob(item['pattern']):
                if path_item.is_file():
                    file_path = str(path_item.resolve()).replace('\\', '/')
                    file_stem = str(path_item.stem)

                    new_item = copy.deepcopy(item)
                    new_item['uri'] = item['uri'].replace('__FILE_PATH__', file_path).replace('__FILE_STEM__', file_stem)

                    new_item.pop('path', None)
                    new_item.pop('pattern', None)

                    Tree.process_item(parent, new_item)

        name = Tree.get_layer_name_from_item(item)

        if name is None:
            return

        layer = Tree.find_layer(parent, name)

        if layer is not None:
            return

        layer = Tree.make_vector(item['uri'], name)

        if not layer.isValid():
            return

        if 'style' in item:
            if 'type' in item['style']:
                if item['style']['type'] == 'line':
                    layer.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple(item['style'])))
                elif item['style']['type'] == 'point':
                    layer.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple(item['style'])))
            else:
                if 'color' in item['style']:
                    symbol = layer.renderer().symbol()
                    symbol.setColor(QColor(item['style']['color']))

                if 'opacity' in item['style']:
                    layer.setOpacity(item['style']['opacity'])

        Utils.add_layer(parent, layer)

    @staticmethod
    @log_call
    def make_vector(uri: str, name: str) -> QgsVectorLayer:
        return QgsVectorLayer(uri, name, 'ogr')

    @staticmethod
    @log_call
    def make_raster(uri: str, name: str) -> QgsRasterLayer:
        return QgsRasterLayer(uri, name, 'wms')

    @staticmethod
    @log_call
    def get_layer_name_from_item(item: dict) -> Optional[str]:
        if 'name' in item:
            return item['name']

        if 'uri' in item:
            if item['uri'].startswith('/vsizip'):
                m = re.search(r'^/vsizip/([^?]+?\.zip)(?=[/\\])', item['uri'], flags=re.IGNORECASE)

                if m is None:
                    return None

                return pathlib.Path(m.group(1)).stem
            else:
                return pathlib.Path(item['uri']).stem

        return None
