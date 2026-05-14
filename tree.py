from .log import log_call
from typing import Optional

from qgis.core import QgsLayerTreeGroup, QgsProject, QgsVectorLayer


class Tree:
    @staticmethod
    @log_call
    def get_root() -> Optional[QgsLayerTreeGroup]:

        root = QgsProject.instance().layerTreeRoot()
        files = root.findGroup('Files')

        if files:
            return files

        return Tree.create_group(root, 'Files', None, 0)

    @staticmethod
    @log_call
    def create_group(parent: QgsLayerTreeGroup, name: str, custom_type: str = None, position: int = -1) -> Optional[QgsLayerTreeGroup]:

        group = parent.addGroup(name)
        group_clone = group.clone()

        if custom_type:
            group_clone.setCustomProperty('type', custom_type)

        parent.insertChildNode(position, group_clone)
        parent.removeChildNode(group)

        return group_clone

    @staticmethod
    @log_call
    def find_group(parent: QgsLayerTreeGroup, name: str) -> Optional[QgsLayerTreeGroup]:

        if not parent:
            return None

        return parent.findGroup(name)

    @staticmethod
    @log_call
    def find_layer(parent: QgsLayerTreeGroup, name: str) -> Optional[QgsVectorLayer]:

        if not parent:
            return None

        for child in parent.children():
            if child.name() == name:
                return child

        return None

    @staticmethod
    @log_call
    def delete_group(group: QgsLayerTreeGroup):

        group.parent().removeChildNode(group)