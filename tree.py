from typing import Optional

from qgis.core import QgsLayerTreeGroup, QgsProject, QgsVectorLayer

from .log import log_call


class Tree:
    @staticmethod
    @log_call
    def get_root() -> Optional[QgsLayerTreeGroup]:
        instance = QgsProject.instance()

        if instance is None:
            return None

        root = instance.layerTreeRoot()

        if root is None:
            return None

        files = root.findGroup('Files')

        if files is not None:
            return files

        return Tree.create_group(root, 'Files', None, 0)

    @staticmethod
    @log_call
    def create_group(parent: QgsLayerTreeGroup, name: str, custom_type: Optional[str] = None, position: int = -1) -> Optional[QgsLayerTreeGroup]:
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
    def find_group(parent: QgsLayerTreeGroup, name: str) -> Optional[QgsLayerTreeGroup]:
        if parent is None:
            return None

        return parent.findGroup(name)

    @staticmethod
    @log_call
    def find_layer(parent: QgsLayerTreeGroup, name: str) -> Optional[QgsVectorLayer]:
        if parent is None:
            return None

        for child in parent.children():
            if child.name() == name:
                return child

        return None

    @staticmethod
    @log_call
    def delete_group(group: QgsLayerTreeGroup) -> None:
        parent = group.parent()

        if parent is not None:
            parent.removeChildNode(group)
