import xml.etree.ElementTree as ET

from typing import Optional

from qgis.core import QgsLayerTree, QgsLayerTreeGroup

from .dialog import Dialog
from .log import log_call
from .segment import Segment
from .string import String
from .tree import Tree


class Track:
    @staticmethod
    @log_call
    def create(file: QgsLayerTreeGroup, name: Optional[str] = None) -> Optional[QgsLayerTreeGroup]:
        tracks = Tree.find_group(file, 'Tracks')

        if not tracks:
            return None

        if not name:
            name = String.generate_name('Track', len(tracks.children()))

        track = Tree.create_group(tracks, name)

        if not track:
            return None

        track.setCustomProperty('type', 'track')

        return track

        # TODO: Try to use data sources.
        # DataSource.set(point_layer, file_name + '?type=waypoint')
        # DataSource.set(path_layer, file_name + '?type=track')

        # TODO: Must be called after setting data source.
        # point_layer.setLabeling(Label.create_settings())

    @staticmethod
    @log_call
    def delete(track: QgsLayerTreeGroup):
        if not track:
            return

        if Dialog.confirm('Delete track?'):
            Tree.delete_group(track)

    @staticmethod
    @log_call
    def get_active(iface) -> Optional[QgsLayerTreeGroup]:
        nodes = iface.layerTreeView().selectedNodes()

        if len(nodes) != 1:
            return None

        node = nodes[0]

        while node.parent() and type(node.parent()) != QgsLayerTree:
            node_type = node.customProperty('type')

            if node_type and node_type == 'track':
                return node

            node = node.parent()

        return None

    @staticmethod
    @log_call
    def refresh(track: QgsLayerTreeGroup):
        if not track:
            return

        for segment in track.children():
            if segment.customProperty('type') == 'segment':
                Segment.refresh(segment)

    @staticmethod
    @log_call
    def reverse(track: QgsLayerTreeGroup):
        if not track:
            return

        for segment in track.children():
            if segment.customProperty('type') == 'segment':
                Segment.reverse(segment)

    @staticmethod
    @log_call
    def optimize(track: QgsLayerTreeGroup):
        if not track:
            return

        for segment in track.children():
            if segment.customProperty('type') == 'segment':
                Segment.optimize(segment)

    @staticmethod
    @log_call
    def from_xml(file: QgsLayerTreeGroup, trk: ET.Element):
        trk_name = trk.find('name')

        if trk_name is not None:
            name = trk_name.text
        else:
            name = None

        track = Track.create(file, name)

        if not track:
            return

        for trkseg in trk.iter('trkseg'):
            Segment.from_xml(track, trkseg)

    @staticmethod
    @log_call
    def to_xml(track: QgsLayerTreeGroup) -> Optional[ET.Element]:
        if not track:
            return None

        name = ET.Element('name')
        name.text = track.name()

        trk = ET.Element('trk')
        trk.append(name)

        for segment in track.children():
            if segment.customProperty('type') != 'segment':
                continue

            trkseg = Segment.to_xml(segment)

            if not trkseg:
                continue

            trk.append(trkseg)

        return trk

    @staticmethod
    @log_call
    def get_distance(track: QgsLayerTreeGroup) -> float:
        if not track:
            return 0.0

        distance = 0.0

        for segment in track.children():
            distance += Segment.get_distance(segment)

        return distance
