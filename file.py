import re
import os
import xml.etree.ElementTree as ET

from typing import Optional

from qgis.core import QgsLayerTree, QgsLayerTreeGroup

from .color import Color
from .dialog import Dialog
from .log import log_call
from .layer import Layer
from .string import String
from .segment import Segment
from .symbol import Symbol
from .track import Track
from .tree import Tree
from .utils import Utils
from .waypoint import Waypoint


class File:
    @staticmethod
    @log_call
    def new(name: Optional[str] = None) -> Optional[QgsLayerTreeGroup]:
        files = Tree.get_or_create_group(Tree.get_root(), 'Tracks')

        if files is None:
            return None

        if name is None:
            name = String.generate_name('File', len(files.children()))

        file = Tree.create_group(files, name, 'file')

        if file is None:
            return None

        waypoints = Tree.create_group(file, 'Waypoints', 'waypoints')

        if waypoints is None:
            return None

        points = Layer.get_or_create_waypoints(waypoints)

        if points is None:
            return None

        Symbol.set(points, Symbol.create_waypoint(Color.random()))

        tracks = Tree.create_group(file, 'Tracks', 'tracks')

        if tracks is None:
            return None

        return file

    @staticmethod
    @log_call
    def open():
        file_name = Dialog.get_file_name()

        if file_name is None:
            return

        File.load_xml(file_name)

    @staticmethod
    @log_call
    def save(file: Optional[QgsLayerTreeGroup], extension_osmand:bool = True):
        if file is None:
            return

        file_name = file.customProperty('fileName')

        if not file_name:
            file_name = Dialog.get_file_name()

            if not file_name:
                return

            file.setName(os.path.basename(file_name))
            file.setCustomProperty('fileName', file_name)

            File.refresh_distance(file)

        waypoints = Tree.find_group(file, 'Waypoints')

        if not waypoints:
            return

        ns_gpx = 'https://www.topografix.com/GPX/1/1'
        ns_osmand = 'https://osmand.net/docs/technical/osmand-file-formats/osmand-gpx'

        ET.register_namespace('', ns_gpx)
        ET.register_namespace('osmand', ns_osmand)

        gpx = ET.Element(f'{{{ns_gpx}}}gpx', version='1.1')

        wpts = Waypoint.to_xml(waypoints)

        for wpt in wpts:
            gpx.append(wpt)

        tracks = Tree.find_group(file, 'Tracks')

        if not tracks:
            return

        for track in tracks.children():
            if track.customProperty('type') != 'track':
                continue

            trk = Track.to_xml(track)

            if not trk:
                continue

            gpx.append(trk)

        if extension_osmand:
            """
            color = ET.Element(f'{{{ns_osmand}}}color')
            color.text = '#33FF33'

            width = ET.Element(f'{{{ns_osmand}}}width')
            width.text = 'bold'

            extensions = ET.Element('extensions')
            extensions.append(color)
            extensions.append(width)

            gpx.append(extensions)
            """

        ET.indent(gpx, space='  ', level=0)

        tree = ET.ElementTree(gpx)
        tree.write(file_name, encoding='utf-8', xml_declaration=True)

    @staticmethod
    @log_call
    def close(file: Optional[QgsLayerTreeGroup], force: bool = False):
        if file is None:
            return

        if force or Dialog.confirm('Close file?'):
            Tree.delete_group(file)

    @staticmethod
    @log_call
    def get_active(iface) -> Optional[QgsLayerTreeGroup]:
        nodes = iface.layerTreeView().selectedNodes()

        if len(nodes) != 1:
            return None

        node = nodes[0]

        while node.parent() and type(node.parent()) != QgsLayerTree:
            node_type = node.customProperty('type')

            if node_type and node_type == 'file':
                return node

            node = node.parent()

        return None

    @staticmethod
    @log_call
    def refresh_distance(file: Optional[QgsLayerTreeGroup]):
        if file is None:
            return

        files = Tree.get_or_create_group(Tree.get_root(), 'Tracks')

        if not files:
            return

        file_name = file.customProperty('fileName')

        if file_name:
            file.setName(f'{os.path.basename(file_name)} [{File.get_distance(file):.2f} km]')
        else:
            file.setName(f'File {len(files.children())} [{File.get_distance(file):.2f} km]')

        tracks = Tree.find_group(file, 'Tracks')

        if tracks:
            for track in tracks.children():
                if track.customProperty('type') != 'track':
                    continue

                Utils.update_distance(track, Track.get_distance(track))

                for segment in track.children():
                    if segment.customProperty('type') != 'segment':
                        continue

                    Utils.update_distance(segment, Segment.get_distance(segment))

    @staticmethod
    @log_call
    def reload(file: Optional[QgsLayerTreeGroup]):
        if file is None:
            return

        file_name = file.customProperty('fileName')

        if file_name is None:
            return

        File.close(file, True)
        File.load_xml(file_name)

    @staticmethod
    def load_xml(file_name: str):
        # load XML
        with open(file_name) as f:
            xml_string = f.read()

        xml_string = re.sub(r'\sxmlns="[^"]+"', '', xml_string, count=1)
        xml_doc = ET.fromstring(xml_string)

        # create file
        file = File.new(os.path.basename(file_name))

        if file is None:
            return

        file.setCustomProperty('fileName', file_name)

        waypoints = Tree.find_group(file, 'Waypoints')

        if not waypoints:
            return

        for wpt in xml_doc.iter('wpt'):
            Waypoint.from_xml(waypoints, wpt)

        # load tracks
        for trk in xml_doc.iter('trk'):
            Track.from_xml(file, trk)

        File.refresh_distance(file)

    @staticmethod
    @log_call
    def get_distance(file: Optional[QgsLayerTreeGroup]) -> float:
        if file is None:
            return 0.0

        tracks = Tree.find_group(file, 'Tracks')

        if not tracks:
            return 0.0

        distance = 0.0

        for track in tracks.children():
            if track.customProperty('type') != 'track':
                continue

            distance += Track.get_distance(track)

        return distance
