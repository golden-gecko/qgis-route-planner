import pathlib

from typing import Optional

from qgis.core import QgsLayerTreeGroup, QgsProject, QgsRasterLayer, QgsVectorLayer
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
    def create_tree_structure() -> None:
        root = Tree.get_root()

        if root is None:
            return

        groups = {
            'Tracks Editable': None,
            'Tracks Read Only': None,
            'Nature': None,
            'Woods': None,
            'Maps': None,
        }

        for name in groups.keys():
            groups[name] = Tree.get_or_create_group(root, name)

        # Tree.create_track_editable(groups['Tracks Editable'])
        # Tree.create_tracks_read_only(groups['Tracks Read Only'])
        # Tree.create_nature(groups['Nature'])
        Tree.create_woods(groups['Woods'])
        # Tree.create_maps(groups['Maps'])

        #54b04a, 3, visited
        #487bb6, 3, planned

        # db1e2a motorcycle
        # 487bb6 car
        # 54b04a bicycle
    @staticmethod
    @log_call
    def create_track_editable(parent: Optional[QgsLayerTreeGroup]) -> None:
        if parent is None:
            return

    @staticmethod
    @log_call
    def create_tracks_read_only(parent: Optional[QgsLayerTreeGroup]) -> None:
        if parent is None:
            return

        for gpx in Config.Tree.Items['Tracks Read Only']:
            if 'path' not in gpx:
                continue

            path = pathlib.Path(gpx['path'])

            if path.is_dir():
                Tree.process_directory(parent, gpx['path'], gpx['content'], gpx['style'])
            elif path.is_file() and path.suffix.lower() == '.gpx':
                Tree.process_file(parent, gpx['path'], gpx['content'], gpx['style'])

    @staticmethod
    @log_call
    def create_nature(parent: Optional[QgsLayerTreeGroup]) -> None:
        if parent is None:
            return

        gdos = [
            'ObszaryChronionegoKrajobrazu',
            'ObszarySpecjalnejOchrony',
            'ParkiKrajobrazowe',
            'ParkiNarodowe',
            'PomnikiPrzyrody',
            'Rezerwaty',
            'SpecjalneObszaryOchrony',
            'StanowiskaDokumentacyjne',
            'UzytkiEkologiczne',
            'ZespolyPrzyrodniczoKrajobrazowe',
        ]

        uri = (
            "contextualWMSLegend=0&"
            "crs=EPSG:2180&"
            "dpiMode=7&"
            "featureCount=10&"
            "format=image/png&"
            "layers=GDOS:__REPLACE__&"
            "&styles=&"
            "url=https://sdi.gdos.gov.pl/wms?"
        )

        nature = {}

        for name in gdos:
            nature[name] = uri.replace('__REPLACE__', name)

        for name, uri in nature.items():
            layer = Tree.find_layer(parent, name)

            if layer is not None:
                continue

            layer = QgsRasterLayer(uri, name, 'wms')

            if not layer.isValid():
                continue

            Utils.add_layer(parent, layer)

    @staticmethod
    @log_call
    def create_woods(parent: Optional[QgsLayerTreeGroup]) -> None:
        if parent is None:
            return

        for gpx in Config.Tree.Items['Woods']:
            if 'path' not in gpx:
                continue

            path = pathlib.Path(gpx['path'])

            if path.is_dir():
                Tree.process_directory(parent, gpx['path'], gpx['content'], gpx['style'])
            elif path.is_file() and (path.suffix.lower() == '.gpx' or path.suffix.lower() == '.zip'):
                Tree.process_file(parent, gpx['path'], gpx['content'], gpx['style'])

    @staticmethod
    @log_call
    def create_maps(parent: Optional[QgsLayerTreeGroup]) -> None:
        if parent is None:
            return

        """
        maps = {
            'Google StreetView': f'type=xyz&url={urllib.parse.quote('https://mts2.google.com/mapslt?lyrs=svv&x={x}&y={y}&z={z}&w=256&h=256&hl=en&style=40,18', safe=':/{}?=%')}',
            'Bing Satellite': f"type=xyz&url={urllib.parse.quote('http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=0&dir=dir_n', safe=':/{}?=&')}&zmin=1&zmax=19",
            'Google Hybrid': f'type=xyz&url={urllib.parse.quote('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', safe=':/{}?=%')}',
            'Google Satellite': f'type=xyz&url={urllib.parse.quote('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', safe=':/{}?=%')}',
            'Google Terrain': f'type=xyz&url={urllib.parse.quote('https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', safe=':/{}?=%')}',
        }

        for name, style in Config.MapBox.Styles.items():
            maps[name] = f'type=xyz&url=https://api.mapbox.com/styles/v1/{style}/tiles/256/{{z}}/{{x}}/{{y}}?access_token={Config.MapBox.Key}'

        maps['OpenStreetMap'] = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        """

        for name, uri in Config.Tree.Items['Maps'].items():
            layer = Tree.find_layer(parent, name)

            if layer is not None:
                continue

            layer = QgsRasterLayer(uri, name, 'wms')

            if not layer.isValid():
                continue

            Utils.add_layer(parent, layer)

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
    def find_layer(parent: Optional[QgsLayerTreeGroup], name: str) -> Optional[QgsVectorLayer]:
        if parent is None:
            return None

        for child in parent.children():
            if child.name() == name:
                return child

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
    def process_directory(parent: Optional[QgsLayerTreeGroup], path_name: str, content: dict, style: dict) -> None:
        if parent is None:
            return

        path = pathlib.Path(path_name)

        directory = Tree.get_or_create_group(parent, path.stem)

        if directory is None:
            return

        for item in path.iterdir():
            if item.is_dir():
                Tree.process_directory(directory, item.resolve(), content, style)
            elif item.is_file() and (item.suffix.lower() == '.gpx' or item.suffix.lower() == '.zip'):
                Tree.process_file(directory, item.resolve(), content, style)

    @staticmethod
    @log_call
    def process_file(parent: Optional[QgsLayerTreeGroup], path_name: str, content: dict, style: dict) -> None:
        if parent is None:
            return

        path = pathlib.Path(path_name)

        layer = Tree.find_layer(parent, path.stem)

        if layer is not None:
            return

        if 'layer' in content:
            layer = QgsVectorLayer(content['layer'].replace('__FILE__PATH__', str(path)).replace('__FILE_STEM__', path.stem), path.stem, "ogr")

            if not layer.isValid():
                return
        elif 'tracks' in content and content['tracks']:
            layer = QgsVectorLayer(f"{path_name}|layername=tracks", path.stem, "ogr")

            if not layer.isValid():
                return

            symbol = layer.renderer().symbol()
            symbol.setColor(QColor(style['color']))
            symbol.setWidth(style['size'])

            line_sl = symbol.symbolLayer(0)
            line_sl.setPenStyle(Qt.DashLine)
        elif 'waypoints' in content and content['waypoints']:
            layer = QgsVectorLayer(f"{path_name}|layername=waypoints", path.stem, "ogr")

            if not layer.isValid():
                return

            symbol = layer.renderer().symbol()
            symbol.setColor(QColor(style['color']))
            symbol.setSize(style['size'])
        else:
            return

        if 'color' in style:
            symbol = layer.renderer().symbol()
            symbol.setColor(QColor(style['color']))

        if 'opacity' in style:
            layer.setOpacity(style['opacity'])

        Utils.add_layer(parent, layer)
