import re
import os
import xml.etree.ElementTree as ET

from typing import Optional

from qgis.core import QgsLayerTree, QgsLayerTreeGroup

from .color import Color
from .layer import Layer
from .symbol import Symbol
from .track import Track
from .tree import Tree
from .utils import Utils
from .waypoint import Waypoint


class File:
    @staticmethod
    def new(name: str=None) -> Optional[QgsLayerTreeGroup]:
        print(f'File::new({name})')

        files = Tree.get_root()

        if not files:
            return None

        if not name:
            name = Utils.generate_name('File', files)

        file = Tree.create_group(files, name, 'file')

        if not file:
            return None

        waypoints = Tree.create_group(file, 'Waypoints', 'waypoints')

        if not waypoints:
            return None

        points = Layer.get_or_create_waypoints(waypoints)

        if not points:
            return None

        Utils.set_symbol(points, Symbol.create_waypoint(Color.random()))

        tracks = Tree.create_group(file, 'Tracks', 'tracks')

        if not tracks:
            return None

        return file

    @staticmethod
    def open():
        print('File::open()')

        # get file name
        file_name = Utils.get_file_name_from_dialog()

        if not file_name:
            return

        # load XML
        with open(file_name) as file:
            xml_string = file.read()

        xml_string = re.sub(r'\sxmlns="[^"]+"', '', xml_string, count=1)
        xml_doc = ET.fromstring(xml_string)

        # create file
        file = File.new(os.path.basename(file_name))

        if not file:
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

    @staticmethod
    def save(file: QgsLayerTreeGroup):
        print(f'File::save({file})')

        if not file:
            return

        file_name = file.customProperty('fileName')

        if not file_name:
            file_name = Utils.get_file_name_from_dialog()

            if not file_name:
                return

        file.setName(os.path.basename(file_name))
        file.setCustomProperty('fileName', file_name)

        waypoints = Tree.find_group(file, 'Waypoints')

        if not waypoints:
            return

        gpx = ET.Element('gpx', version='1.0', xmlns='http://www.topografix.com/GPX/1/0')

        wpts = Waypoint.to_xml(waypoints)

        for wpt in wpts:
            gpx.append(wpt)

        tracks = Tree.find_group(file, 'Tracks')

        if not tracks:
            return None

        for track in tracks.children():
            if track.customProperty('type') != 'track':
                continue

            trk = Track.to_xml(track)

            if not trk:
                continue

            gpx.append(trk)

        ET.indent(gpx, space='  ', level=0)

        tree = ET.ElementTree(gpx)
        tree.write(file_name)

    @staticmethod
    def close(file: QgsLayerTreeGroup):
        print(f'File::close({file})')

        if not file:
            return

        if Utils.confirm('Close file?'):
            Tree.delete_group(file)

    @staticmethod
    def get_active(iface) -> Optional[QgsLayerTreeGroup]:
        print('File::get_active()')

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
