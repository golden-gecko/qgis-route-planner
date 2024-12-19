from typing import Optional

from qgis.core import QgsLayerTreeGroup, QgsProject, QgsVectorLayer


class Tree:
    @staticmethod
    def get_root():
        print('Tree::get_root()')

        root = QgsProject.instance().layerTreeRoot()
        files = root.findGroup('Files')

        if files:
            return files

        return Tree.create_group(root, 'Files', None, 0)

    @staticmethod
    def create_group(parent: QgsLayerTreeGroup, name: str, custom_type: str = None, position: int = -1) -> Optional[QgsLayerTreeGroup]:
        print(f'Tree::create_group({parent}, {name})')

        group = parent.addGroup(name)
        group_clone = group.clone()

        if custom_type:
            group_clone.setCustomProperty('type', custom_type)

        parent.insertChildNode(position, group_clone)
        parent.removeChildNode(group)

        return group_clone

    @staticmethod
    def find_group(parent: QgsLayerTreeGroup, name: str) -> Optional[QgsLayerTreeGroup]:
        print(f'Tree::find_group({parent}, {name})')

        if not parent:
            return None

        return parent.findGroup(name)

    @staticmethod
    def find_layer(parent: QgsLayerTreeGroup, name: str) -> Optional[QgsVectorLayer]:
        print(f'Tree::find_layer({parent}, {name})')

        if not parent:
            return None

        for child in parent.children():
            if child.name() == name:
                return child

        return None

    @staticmethod
    def delete_group(group: QgsLayerTreeGroup):
        print(f'Tree::delete_group({group})')

        group.parent().removeChildNode(group)
