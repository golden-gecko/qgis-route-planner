import os

from typing import Optional

from qgis.core import QgsDistanceArea, QgsFeature, QgsField, QgsLayerTree, QgsLayerTreeGroup, QgsPoint, QgsPointXY, QgsProject, QgsVectorLayer, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QFileDialog

from .color import Color
from .google import Google
from .iface import Iface
from .options import Options
from .point import Point
from .symbol import Symbol
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
        track = Utils.create_directory()

        if not track:
            return None

        color = Color.random()

        point_layer = Track.get_or_create_point_layer(track)
        path_layer = Track.get_or_create_path_layer(track)

        Utils.set_symbol(point_layer, Symbol.create_point(color))
        Utils.set_symbol(path_layer, Symbol.create_path(color))

        # Utils.set_data_source(point_layer, file_name + '?type=waypoint')
        # Utils.set_data_source(path_layer, file_name + '?type=track')

        # TODO: Must be after setting data source. Fix.
        # point_layer.setLabeling(Utils.create_label_settings())

        return track
        """

    @staticmethod
    def delete(track: QgsLayerTreeGroup):
        print(f'Track::delete({track})')

        Tree.delete_group(track)

    @staticmethod
    def open():
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(['GPX files (*.gpx)'])

        if not dialog.exec_():
            return None

        if len(dialog.selectedFiles()) != 1:
            return None

        file_name = dialog.selectedFiles()[0]

        track = Track.create()

        if not track:
            return

        point_layer = Track.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Track.get_or_create_path_layer(track)

        if not path_layer:
            return

        print(file_name)

        with open(file_name) as f:
            xmlstring = f.read()

        xmlstring = re.sub(r'\sxmlns="[^"]+"', '', xmlstring, count=1)

        gpx = ET.fromstring(xmlstring)

        point_layer.startEditing()

        for wpt in gpx.iter('wpt'):
            point_layer.addFeature(Point.create_feature(QgsPoint(float(wpt.get('lon')), float(wpt.get('lat'))), point_layer.fields()))

        Utils.refresh_position(point_layer)

        point_layer.commitChanges()

        path_layer.startEditing()

        for trk in gpx.iter('trk'):
            for trkseg in trk.iter('trkseg'):
                points = []

                for trkpt in trkseg.iter('trkpt'):
                    points.append((float(trkpt.get('lon')), float(trkpt.get('lat'))))

                path_layer.addFeature(Utils.create_polyline(points))

        path_layer.commitChanges()

    @staticmethod
    def save():
        track = Track.get_active(Iface.get())

        if not track:
            return

        point_layer = Track.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Track.get_or_create_path_layer(track)

        if not path_layer:
            return

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(['GPX files (*.gpx)'])

        if not dialog.exec_():
            return None

        if len(dialog.selectedFiles()) != 1:
            return None

        file_name = dialog.selectedFiles()[0]
        _, file_ext = os.path.splitext(file_name)

        if len(file_ext) == 0:
            file_name += '.gpx'

        gpx = ET.Element('gpx')

        for feature in point_layer.getFeatures():
            point = feature.geometry().asPoint()

            ET.SubElement(gpx, 'wpt', lat=str(point.y()), lon=str(point.x()))

        trk = ET.SubElement(gpx, 'trk')

        for feature in path_layer.getFeatures():
            for part in feature.geometry().parts():
                trkseg = ET.SubElement(trk, 'trkseg')

                for vertex in part.vertices():
                    ET.SubElement(trkseg, 'trkpt', lat=str(vertex.y()), lon=str(vertex.x()))

        ET.indent(gpx, space='  ', level=0)

        tree = ET.ElementTree(gpx)
        tree.write(file_name)

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
        point_layer = Track.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Track.get_or_create_path_layer(track)

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
    def refresh_point_create_start(track: QgsLayerTreeGroup, position: int):
        print(f'Track::refresh_point_create_start(f{track}, {position})')

        point_layer = Track.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Track.get_or_create_path_layer(track)

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

            Track.refesh_segment(path_layer, position, a, b)

        # add middle segment
        elif previous_point and current_point and next_point:
            pass

        # add last segment
        elif previous_point and current_point and not next_point:
            pass

    @staticmethod
    def refresh_point_create_middle(track: QgsLayerTreeGroup, position: int):
        print(f'Track::refresh_point_create_middle(f{track}, {position})')

        point_layer = Track.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Track.get_or_create_path_layer(track)

        if not path_layer:
            return

        previous_point = Track.get(point_layer, position - 1)
        current_point = Track.get(point_layer, position)
        next_point = Track.get(point_layer, position + 1)

        # move first segment
        if not previous_point and current_point and next_point:
            pass

        # move middle segment
        elif previous_point and current_point and next_point:
            path_layer.startEditing()

            geometries = []

            for local_position, feature in enumerate(path_layer.getFeatures(), start=1):
                geometries.append(feature.geometry())

                if local_position == position - 1:
                    geometries.append(Utils.create_polyline_geometry([(0, 0)]))

                print(f'local_position: {local_position}, position: {position}')

                path_layer.deleteFeature(feature.id())

            for geometry in geometries:
                feature = QgsFeature(path_layer.fields())
                feature.setGeometry(geometry)

                path_layer.addFeature(feature)

            path_layer.commitChanges()

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
            pass

    @staticmethod
    def refresh_point_create_end(track: QgsLayerTreeGroup, position: int):
        print(f'Track::refresh_point(f{track}, {position})')

        point_layer = Track.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Track.get_or_create_path_layer(track)

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
    def refresh_point_move(track: QgsLayerTreeGroup, position: int):
        print(f'Track::refresh_point_move(f{track}, {position})')

        point_layer = Track.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Track.get_or_create_path_layer(track)

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
    def refresh_point_delete(track: QgsLayerTreeGroup, position: int):
        print(f'Track::refresh_point_delete(f{track}, {position})')

        point_layer = Track.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Track.get_or_create_path_layer(track)

        if not path_layer:
            return

        previous_point = Track.get(point_layer, position - 1)
        current_point = Track.get(point_layer, position)

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
    def refesh_segment(layer: QgsVectorLayer, position: int, a: QgsPointXY, b: QgsPointXY):
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
    def get(layer: QgsVectorLayer, position) -> Optional[QgsFeature]:
        print(f'Track::get(f{layer}, {position})')

        for local_position, feature in enumerate(layer.getFeatures(), start=1):
            if local_position == position:
                return feature

        return None

    @staticmethod
    def get_path(layer: QgsVectorLayer, position: int):
        print(f'Track::get_path(f{layer}, {position})')

        for index, feature in enumerate(layer.getFeatures(), start=1):
            if index == position:
                return feature

        return None

    @staticmethod
    def get_or_create_point_layer(track: QgsLayerTreeGroup) -> Optional[QgsVectorLayer]:
        print(f'Utils::get_or_create_point_layer({track})')

        if not track:
            return None

        for child in track.children():
            if child.layer() and child.layer().name() == 'Point':
                return child.layer()

        layer = QgsVectorLayer('Point', 'Point', 'memory')
        layer.startEditing()
        layer.setLabelsEnabled(True)
        layer.setLabeling(Utils.create_label_settings())

        Utils.set_crs(layer, 'EPSG:4326')

        provider = layer.dataProvider()
        provider.addAttributes([QgsField('position', QVariant.Int)])

        layer.commitChanges()

        QgsProject.instance().addMapLayer(layer, False)

        node = track.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer

    @staticmethod
    def get_or_create_path_layer(track: QgsLayerTreeGroup) -> Optional[QgsVectorLayer]:
        print(f'Utils::get_or_create_path_layer({track})')

        if not track:
            return None

        for child in track.children():
            if child.layer() and child.layer().name() == 'Path':
                return child.layer()

        layer = QgsVectorLayer('MultiLineStringZ', 'Path', 'memory')

        Utils.set_crs(layer, 'EPSG:4326')

        QgsProject.instance().addMapLayer(layer, False)

        node = track.addLayer(layer)

        if node:
            node.setCustomProperty('showFeatureCount', True)

        return layer
