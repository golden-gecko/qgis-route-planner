from qgis.core import QgsDistanceArea, QgsLayerTreeGroup, QgsLineSymbol, QgsWkbTypes

from .color import Color
from .google import Google
from .symbol import Symbol
from .utils import Utils


class Track:
    @staticmethod
    def add(iface):
        tracks = Utils.get_or_create_tracks_directory()

        if not tracks:
            return

        track = Utils.create_directory(tracks, Track.generate_name(tracks))

        if not track:
            return

        color = Color.random()

        point_layer = Utils.get_or_create_point_layer(track)
        point_layer.startEditing()
        point_layer.renderer().symbol().setColor(color)
        point_layer.commitChanges()

        path_layer = Utils.get_or_create_path_layer(track)
        path_layer.startEditing()
        path_layer.renderer().setSymbol(Symbol.create_dashed_line(color))
        path_layer.commitChanges()

    @staticmethod
    def delete(iface):
        tracks = Utils.get_or_create_tracks_directory()

        if not tracks:
            return

        track = Track.get_active(iface)

        if not track:
            return

        tracks.removeChildNode(track)

    @staticmethod
    def generate_name(tracks: QgsLayerTreeGroup) -> str:
        return f'Track {len(tracks.children()) + 1}'

    @staticmethod
    def get_active(iface) -> QgsLayerTreeGroup|None:
        nodes = iface.layerTreeView().selectedNodes()

        if len(nodes) != 1:
            return None

        node = nodes[0]

        if node.parent() and node.parent().name() == 'Tracks':
            return node

        if node.name() in [Utils.LAYER_NAME_PATH, Utils.LAYER_NAME_POINT]:
            return node.parent()

        return None

    @staticmethod
    def get_length(track) -> float:
        path_layer = Utils.get_or_create_path_layer(track)

        if not path_layer:
            return 0.0

        d = QgsDistanceArea()
        d.setEllipsoid('WGS84')

        return sum([d.measureLength(feature.geometry()) for feature in path_layer.getFeatures()]) / 1000.0

    @staticmethod
    def refresh(track):
        point_layer = Utils.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Utils.get_or_create_path_layer(track)

        if not path_layer:
            return

        points = []

        for feature in point_layer.getFeatures():
            if feature.geometry().type() == QgsWkbTypes.PointGeometry:
                points.append((feature.geometry().asPoint().x(), feature.geometry().asPoint().y()))

        if not points:
            return

        path = []

        for i in range(len(points) - 1):
            path_points = Google.get_direction_as_points(f'{points[i][1]} {points[i][0]}', f'{points[i + 1][1]} {points[i + 1][0]}')

            if not path_points:
                continue

            print(f'Track::refresh() - Got {len(path_points)} points')

            path.append(path_points)

        Utils.update_layer(point_layer, path_layer, path)

    @staticmethod
    def refresh_active(iface):
        tracks = Utils.get_or_create_tracks_directory()

        if not tracks:
            return

        track = Track.get_active(iface)

        if not track:
            return

        Track.refresh(track)
