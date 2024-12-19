from typing import Optional

from qgis.core import QgsDistanceArea, QgsFeature, QgsField, QgsLayerTree, QgsLayerTreeGroup, QgsPointXY, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant

from .google import Google
from .options import Options
from .segment import Segment
from .tree import Tree
from .utils import Utils


class Track:
    @staticmethod
    def create(file: QgsLayerTreeGroup) -> Optional[QgsLayerTreeGroup]:
        print(f'Track::create({file})')

        tracks = Tree.find_group(file, 'Tracks')

        if not tracks:
            return None

        track = Tree.create_group(tracks, Utils.generate_name('Track', tracks))

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
    def get_length(track: QgsLayerTreeGroup) -> float:
        path_layer = Track.get_or_create_path_layer(track)

        if not path_layer:
            return 0.0

        d = QgsDistanceArea()
        d.setEllipsoid('WGS84')

        return sum([d.measureLength(feature.geometry()) for feature in path_layer.getFeatures()]) / 1000.0

    @staticmethod
    def refresh(track: QgsLayerTreeGroup):
        for segment in track.children():
            if segment.customProperty('type') == 'segment':
                Segment.refresh(segment)
