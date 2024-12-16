import os
import re
import xml.etree.ElementTree as ET

from typing import Optional

from qgis.core import QgsLayerTree, QgsLayerTreeGroup

from .layer import Layer
from .segment import Segment
from .point import Point
from .track import Track
from .tree import Tree
from .utils import Utils
from .waypoint import Waypoint


class File:
    @staticmethod
    def new(name: str=None) -> Optional[QgsLayerTreeGroup]:
        print('File::new()')

        files = Tree.get_root()

        if not files:
            return None

        if not name:
            name = Utils.generate_name('File', files)

        file = Tree.create_group(files, name)

        if not file:
            return None

        file.setCustomProperty('type', 'file')

        waypoints = Tree.create_group(file, 'Waypoints')

        if not waypoints:
            return None

        waypoints.setCustomProperty('type', 'waypoints')

        Layer.create_points(waypoints)

        tracks = Tree.create_group(file, 'Tracks')

        if not tracks:
            return None

        tracks.setCustomProperty('type', 'tracks')

        return file

    @staticmethod
    def open():
        print('File::open()')

        file_name = Utils.get_file_name_from_dialog()

        if not file_name:
            return

        name, _ = os.path.splitext(file_name)

        with open(file_name) as file:
            xml_string = file.read()

        xml_string = re.sub(r'\sxmlns="[^"]+"', '', xml_string, count=1)
        xml_doc = ET.fromstring(xml_string)

        file = File.new(os.path.basename(name))

        for wpt in xml_doc.iter('wpt'):
            Waypoint.create(file, float(wpt.get('lon')), float(wpt.get('lat')))

        for trk in xml_doc.iter('trk'):
            track = Track.create(file)

            for trkseg in trk.iter('trkseg'):
                segment = Segment.create(track)

                for trkpt in trkseg.iter('trkpt'):
                    Point.create(segment, float(trkpt.get('lon')), float(trkpt.get('lat')))

    @staticmethod
    def save(file: QgsLayerTreeGroup):
        print('File::save()')

    @staticmethod
    def close(file: QgsLayerTreeGroup):
        print('File::close()')

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
