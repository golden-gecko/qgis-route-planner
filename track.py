from typing import Optional

from qgis.core import QgsDistanceArea, QgsFeature, QgsLayerTreeGroup, QgsWkbTypes

from .color import Color
from .google import Google
from .options import Options
from .symbol import Symbol
from .utils import Utils


class Track:
    @staticmethod
    def create():
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
    def edit(iface):
        tracks = Utils.get_or_create_tracks_directory()

        if not tracks:
            return

        track = Track.get_active(iface)

        if not track:
            return

    @staticmethod
    def generate_name(tracks: QgsLayerTreeGroup) -> str:
        return f'Track {len(tracks.children()) + 1}'

    @staticmethod
    def get_active(iface) -> Optional[QgsLayerTreeGroup]:
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

        if Options.routing:
            for i in range(len(points) - 1):
                path_points = Google.get_direction_as_points(f'{points[i][1]} {points[i][0]}', f'{points[i + 1][1]} {points[i + 1][0]}')

                if not path_points:
                    continue

                print(f'Track::refresh() - Got {len(path_points)} points')

                path.append(path_points)
        else:
            for i in range(len(points) - 1):
                path.append([points[i], points[i + 1]])

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

    @staticmethod
    def refresh_point_create_start(track, position):
        print(f'Track::refresh_point_create_start(f{track}, {position})')

        point_layer = Utils.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Utils.get_or_create_path_layer(track)

        if not path_layer:
            return

        previous_point = Track.get(point_layer, position - 1)
        current_point = Track.get(point_layer, position)
        next_point = Track.get(point_layer, position + 1)

        path_layer.startEditing()

        geometries = [
            Utils.create_polyline_geometry([(0, 0)])
        ]

        for feature in path_layer.getFeatures():
            geometries.append(feature.geometry())
            path_layer.deleteFeature(feature.id())

        for geometry in geometries:
            feature = QgsFeature(path_layer.fields())
            feature.setGeometry(geometry)

            path_layer.addFeature(feature)

        path_layer.commitChanges()

        # add first segment
        if not previous_point and current_point and next_point:
            a = current_point.geometry().asPoint()
            b = next_point.geometry().asPoint()

            print('current_point', current_point.attributes())
            print('next_point', next_point.attributes())

            Track.refesh_segment(path_layer, position, a, b)

        # add middle segment
        elif previous_point and current_point and next_point:
            pass

        # add last segment
        elif previous_point and current_point and not next_point:
            pass

    @staticmethod
    def refresh_point_create_end(track, position):
        print(f'Track::refresh_point(f{track}, {position})')

        point_layer = Utils.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Utils.get_or_create_path_layer(track)

        if not path_layer:
            return

        previous_point = Track.get(point_layer, position - 1)
        current_point = Track.get(point_layer, position)
        next_point = Track.get(point_layer, position + 1)

        # add first segment
        if not previous_point and current_point and next_point:
            pass

        # add middle segment
        elif previous_point and current_point and next_point:
            pass

        # add last segment
        elif previous_point and current_point and not next_point:
            a = previous_point.geometry().asPoint()
            b = current_point.geometry().asPoint()

            if Options.routing:
                segment_points = Google.get_direction_as_points(f'{a.y()} {a.x()}', f'{b.y()} {b.x()}')

                if not segment_points:
                    return
            else:
                segment_points = [a, b]

            vl = path_layer
            pr = vl.dataProvider()
            vl.startEditing()

            pr.addFeature(Utils.create_polyline(segment_points))
            vl.commitChanges()

    @staticmethod
    def refresh_point_move(track, position):
        print(f'Track::refresh_point_move(f{track}, {position})')

        point_layer = Utils.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Utils.get_or_create_path_layer(track)

        if not path_layer:
            return

        previous_point = Track.get(point_layer, position - 1)
        current_point = Track.get(point_layer, position)
        next_point = Track.get(point_layer, position + 1)

        # move first segment
        if not previous_point and current_point and next_point:
            a = current_point.geometry().asPoint()
            b = next_point.geometry().asPoint()

            Track.refesh_segment(path_layer, position, a, b)

        # move middle segment
        elif previous_point and current_point and next_point:
            # previous segment
            a = previous_point.geometry().asPoint()
            b = current_point.geometry().asPoint()

            Track.refesh_segment(path_layer, position - 1, a, b)

            # next segment
            a = current_point.geometry().asPoint()
            b = next_point.geometry().asPoint()

            Track.refesh_segment(path_layer, position, a, b)

        # move last segment
        elif previous_point and current_point and not next_point:
            a = previous_point.geometry().asPoint()
            b = current_point.geometry().asPoint()

            Track.refesh_segment(path_layer, position - 1, a, b)

    @staticmethod
    def refresh_point_delete(track, position):
        print(f'Track::refresh_point_delete(f{track}, {position})')

        point_layer = Utils.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Utils.get_or_create_path_layer(track)

        if not path_layer:
            return

        previous_point = Track.get(point_layer, position - 1)
        current_point = Track.get(point_layer, position)
        next_point = Track.get(point_layer, position + 1)

        # delete first segment
        if position == 1:
            feature = Track.get_path(path_layer, position)

            if feature:
                path_layer.startEditing()
                path_layer.deleteFeature(feature.id())
                path_layer.commitChanges()

        # delete last segment
        elif position - 1 == point_layer.featureCount():
            feature = Track.get_path(path_layer, position - 1)

            if feature:
                path_layer.startEditing()
                path_layer.deleteFeature(feature.id())
                path_layer.commitChanges()

        # delete middle segment
        elif previous_point and current_point:
            a = previous_point.geometry().asPoint()
            b = current_point.geometry().asPoint()

            Track.refesh_segment(path_layer, position - 1, a, b)

            feature = Track.get_path(path_layer, position)

            path_layer.startEditing()
            path_layer.deleteFeature(feature.id())
            path_layer.commitChanges()

    @staticmethod
    def refesh_segment(layer, position, a, b):
        if Options.routing:
            segment_points = Google.get_direction_as_points(f'{a.y()} {a.x()}', f'{b.y()} {b.x()}')

            if not segment_points:
                return
        else:
            segment_points = [a, b]

        vl = layer
        vl.startEditing()

        feature = Track.get_path(layer, position)

        layer.startEditing()
        layer.changeGeometry(feature.id(), Utils.create_polyline_geometry(segment_points))
        layer.commitChanges()

    @staticmethod
    def get(layer, position) -> Optional[QgsFeature]:
        print(f'Track::get(f{layer}, {position})')

        for feature in layer.getFeatures():
            if feature.attribute('position') == position:
                return feature

        return None

    @staticmethod
    def get_path(layer, position):
        print(f'Track::get_path(f{layer}, {position})')

        for index, feature in enumerate(layer.getFeatures(), start=1):
            if index == position:
                return feature

        return None
