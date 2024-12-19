import os
import re
import xml.etree.ElementTree as ET

from typing import Optional

from qgis.core import QgsLayerTree, QgsLayerTreeGroup

from .layer import Layer
from .path import Path
from .segment import Segment
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

        file = Tree.create_group(files, name, 'file')

        if not file:
            return None

        waypoints = Tree.create_group(file, 'Waypoints', 'waypoints')

        if not waypoints:
            return None

        points = Layer.get_or_create_points(waypoints)

        if not points:
            return None

        tracks = Tree.create_group(file, 'Tracks', 'tracks')

        if not tracks:
            return None

        return file

    @staticmethod
    def open():
        print('File::open()')

        """
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

                points = [(float(trkpt.get('lon')), float(trkpt.get('lat'))) for trkpt in trkseg.iter('trkpt')]

                Path.create(segment, points)
        """

        """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(['GPX files (*.gpx)'])

        if not dialog.exec_():
            return None

        if len(dialog.selectedFiles()) != 1:
            return None

        file_name = dialog.selectedFiles()[0]

        track = Track.create()

        if not track:
            return

        point_layer = Track.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Track.get_or_create_path_layer(track)

        if not path_layer:
            return

        print(file_name)

        with open(file_name) as f:
            xmlstring = f.read()

        xmlstring = re.sub(r'\sxmlns="[^"]+"', '', xmlstring, count=1)

        gpx = ET.fromstring(xmlstring)

        point_layer.startEditing()

        for wpt in gpx.iter('wpt'):
            point_layer.addFeature(Point.create_feature(QgsPoint(float(wpt.get('lon')), float(wpt.get('lat'))), point_layer.fields()))

        Utils.refresh_position(point_layer)

        point_layer.commitChanges()

        path_layer.startEditing()

        for trk in gpx.iter('trk'):
            for trkseg in trk.iter('trkseg'):
                points = []

                for trkpt in trkseg.iter('trkpt'):
                    points.append((float(trkpt.get('lon')), float(trkpt.get('lat'))))

                path_layer.addFeature(Utils.create_polyline(points))

        path_layer.commitChanges()
        """

    @staticmethod
    def save(file: QgsLayerTreeGroup):
        print('File::save()')

        """
        track = Track.get_active(Iface.get())

        if not track:
            return

        point_layer = Track.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Track.get_or_create_path_layer(track)

        if not path_layer:
            return

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(['GPX files (*.gpx)'])

        if not dialog.exec_():
            return None

        if len(dialog.selectedFiles()) != 1:
            return None

        file_name = dialog.selectedFiles()[0]
        _, file_ext = os.path.splitext(file_name)

        if len(file_ext) == 0:
            file_name += '.gpx'

        gpx = ET.Element('gpx')

        for feature in point_layer.getFeatures():
            point = feature.geometry().asPoint()

            ET.SubElement(gpx, 'wpt', lat=str(point.y()), lon=str(point.x()))

        trk = ET.SubElement(gpx, 'trk')

        for feature in path_layer.getFeatures():
            for part in feature.geometry().parts():
                trkseg = ET.SubElement(trk, 'trkseg')

                for vertex in part.vertices():
                    ET.SubElement(trkseg, 'trkpt', lat=str(vertex.y()), lon=str(vertex.x()))

        ET.indent(gpx, space='  ', level=0)

        tree = ET.ElementTree(gpx)
        tree.write(file_name)
        """

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
