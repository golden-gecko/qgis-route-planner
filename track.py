import xml.etree.ElementTree as ET

from typing import Optional

from qgis.core import QgsLayerTree, QgsLayerTreeGroup

from .segment import Segment
from .tree import Tree
from .utils import Utils


class Track:
    @staticmethod
    def create(file: QgsLayerTreeGroup, name: str=None) -> Optional[QgsLayerTreeGroup]:
        print(f'Track::create({file}, {name})')

        tracks = Tree.find_group(file, 'Tracks')

        if not tracks:
            return None

        if not name:
            name = Utils.generate_name('Track', len(tracks.children()))

        track = Tree.create_group(tracks, name)

        if not track:
            return None

        track.setCustomProperty('type', 'track')

        return track

        """
        # TODO: Try to use data sources.
        # Utils.set_data_source(point_layer, file_name + '?type=waypoint')
        # Utils.set_data_source(path_layer, file_name + '?type=track')

        # TODO: Must be called after setting data source.
        # point_layer.setLabeling(Utils.create_label_settings())
        """

    @staticmethod
    def delete(track: QgsLayerTreeGroup):
        print(f'Track::delete({track})')

        if not track:
            return

        if Utils.confirm('Delete track?'):
            Tree.delete_group(track)

    @staticmethod
    def get_active(iface) -> Optional[QgsLayerTreeGroup]:
        print('Track::get_active()')

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
    def refresh(track: QgsLayerTreeGroup):
        print(f'Track::refresh({track})')

        for segment in track.children():
            if segment.customProperty('type') == 'segment':
                Segment.refresh(segment)

    @staticmethod
    def optimize(track: QgsLayerTreeGroup):
        print(f'Track::optimize({track})')

        for segment in track.children():
            if segment.customProperty('type') == 'segment':
                Segment.optimize(segment)

    @staticmethod
    def from_xml(file: QgsLayerTreeGroup, trk: ET.Element):
        print(f'Track::from_xml{file}, {trk})')

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
    def to_xml(track: QgsLayerTreeGroup) -> Optional[ET.Element]:
        print(f'Track::to_xml{track})')

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
    def get_distance(track: QgsLayerTreeGroup) -> float:
        print(f'Track::get_distance{track})')

        if not track:
            return 0.0

        distance = 0.0

        for segment in track.children():
            distance += Segment.get_distance(segment)

        return distance
