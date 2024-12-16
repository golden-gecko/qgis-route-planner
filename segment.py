from typing import Optional

from qgis.core import QgsLayerTree, QgsLayerTreeGroup

from .layer import Layer
from .tree import Tree
from .utils import Utils


class Segment:
    @staticmethod
    def create(track: QgsLayerTreeGroup) -> Optional[QgsLayerTreeGroup]:
        print(f'Segment::create({track})')

        if not track:
            return None

        segment = Tree.create_group(track, Utils.generate_name('Segment', track))

        if not segment:
            return None

        segment.setCustomProperty('type', 'segment')

        Layer.create_points(segment)
        Layer.create_paths(segment)

        return segment

    @staticmethod
    def refresh(segment: QgsLayerTreeGroup):
        pass

    @staticmethod
    def delete(segment: QgsLayerTreeGroup):
        print(f'Segment::delete({segment})')

        Tree.delete_group(segment)

    @staticmethod
    def get_active(iface) -> Optional[QgsLayerTreeGroup]:
        print('Segment::get_active()')

        nodes = iface.layerTreeView().selectedNodes()

        if len(nodes) != 1:
            return None

        node = nodes[0]

        while node.parent() and type(node.parent()) != QgsLayerTree:
            node_type = node.customProperty('type')

            if node_type and node_type == 'segment':
                return node

            node = node.parent()

        return None
