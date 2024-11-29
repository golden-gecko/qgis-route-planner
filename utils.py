from qgis.core import QgsFeature, QgsGeometry, QgsLayerTreeGroup, QgsPoint, QgsProject, QgsVectorLayer


class Utils:
    LAYER_NAME_POINT = 'Point'
    LAYER_NAME_PATH = 'Path'

    @staticmethod
    def generate_track_name(tracks: QgsLayerTreeGroup) -> str:
        return f'Track {len(tracks.children()) + 1}'

    @staticmethod
    def get_or_create_point_layer(track: QgsLayerTreeGroup) -> QgsVectorLayer | None:
        print('RoutePlanner::get_or_create_point_layer()')

        for child in track.children():
            if child.layer() and child.layer().name() == Utils.LAYER_NAME_POINT:
                return child.layer()

        layer = QgsVectorLayer('Point', Utils.LAYER_NAME_POINT, 'memory')
        QgsProject.instance().addMapLayer(layer, False)

        node = track.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer

    @staticmethod
    def get_or_create_path_layer(track) -> QgsVectorLayer|None:
        print('RoutePlanner::get_or_create_path_layer()')

        for child in track.children():
            if child.layer() and child.layer().name() == Utils.LAYER_NAME_PATH:
                return child.layer()

        layer = QgsVectorLayer('LineString', Utils.LAYER_NAME_PATH, 'memory')
        QgsProject.instance().addMapLayer(layer, False)

        node = track.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer

    @staticmethod
    def get_parent_name(layer: QgsVectorLayer) -> str|None:
        tree_parent = Utils.get_parent(layer)

        if not tree_parent:
            return None

        return tree_parent.name()

    @staticmethod
    def get_parent(layer: QgsVectorLayer):
        print('RoutePlanner::get_parent()')

        tree_layer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())

        if not tree_layer:
            return None

        tree_parent = tree_layer.parent()

        if not tree_parent:
            return None

        return tree_parent

    @staticmethod
    def get_or_create_tracks_directory() -> QgsLayerTreeGroup:
        print('RoutePlanner::get_or_create_tracks_directory()')

        root = QgsProject.instance().layerTreeRoot()
        routes = root.findGroup('Tracks')

        if not routes:
            routes = root.addGroup('Tracks')
            clone = routes.clone()
            root.insertChildNode(0, clone)
            root.removeChildNode(routes)
            routes = clone

        return routes

    @staticmethod
    def create_track_directory(routes: QgsLayerTreeGroup, name: str):
        print('RoutePlanner::create_track_directory()')

        root = QgsProject.instance().layerTreeRoot()
        route = root.addGroup(name)
        clone = route.clone()
        routes.insertChildNode(-1, clone)
        root.removeChildNode(route)

        return clone

    @staticmethod
    def create_point(point) -> QgsFeature:
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPoint(point))

        return feature

    @staticmethod
    def create_polyline(points) -> QgsFeature:
        point_list = [
            QgsPoint(p[0], p[1]) for p in points
        ]

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolyline(point_list))

        return feature
