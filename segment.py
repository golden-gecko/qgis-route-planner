import math
import xml.etree.ElementTree as ET

from typing import Optional

from qgis.core import QgsFeature, QgsLayerTree, QgsLayerTreeGroup, QgsPoint, QgsPointXY, QgsVectorLayer

from .color import Color
from .google import Google
from .layer import Layer
from .options import Options
from .point import Point
from .symbol import Symbol
from .tree import Tree
from .utils import Utils


class Segment:
    @staticmethod
    def create(track: QgsLayerTreeGroup) -> Optional[QgsLayerTreeGroup]:
        print(f'Segment::create({track})')

        if not track:
            return None

        segment = Tree.create_group(track, Utils.generate_name('Segment', track), 'segment')

        if not segment:
            return None

        points = Layer.get_or_create_points(segment)
        paths = Layer.get_or_create_paths(segment)

        color = Color.random()

        Utils.set_symbol(points, Symbol.create_point(color))
        Utils.set_symbol(paths, Symbol.create_path(color))

        return segment

    @staticmethod
    def refresh(segment: QgsLayerTreeGroup):
        print(f'Segment::refresh({segment})')

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return

        vertices = []

        for feature in points.getFeatures():
            vertices.append((feature.geometry().asPoint().x(), feature.geometry().asPoint().y()))

        if not vertices:
            return

        lines = []

        if Options.routing:
            for i in range(len(vertices) - 1):
                results = Google.get_direction_as_points(f'{vertices[i][1]} {vertices[i][0]}', f'{vertices[i + 1][1]} {vertices[i + 1][0]}')

                if not results:
                    continue

                lines.append(results)
        else:
            for i in range(len(vertices) - 1):
                lines.append([vertices[i], vertices[i + 1]])

        Utils.update_layer(points, paths, lines)

    @staticmethod
    def delete(segment: QgsLayerTreeGroup):
        print(f'Segment::delete({segment})')

        if not segment:
            return

        if Utils.confirm('Delete segment?'):
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

    @staticmethod
    def refresh_point(segment: QgsLayerTreeGroup, position: int):
        print(f'Segment::refresh_point(f{segment}, {position})')

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return

        previous_point = Segment.get_point(points, position - 1)
        current_point = Segment.get_point(points, position)
        next_point = Segment.get_point(points, position + 1)

        # refresh first
        if not previous_point and current_point and next_point:
            a = current_point.geometry().asPoint()
            b = next_point.geometry().asPoint()

            geometries = [
                Utils.create_polyline_geometry([(0, 0)])
            ]

            paths.startEditing()

            for feature in paths.getFeatures():
                geometries.append(feature.geometry())
                paths.deleteFeature(feature.id())

            for geometry in geometries:
                feature = QgsFeature(paths.fields())
                feature.setGeometry(geometry)

                paths.addFeature(feature)

            paths.commitChanges()

            Segment.refesh_segment(paths, 1, a, b)

        # refresh middle
        elif previous_point and current_point and next_point:
            a = previous_point.geometry().asPoint()
            b = current_point.geometry().asPoint()
            c = next_point.geometry().asPoint()

            geometries = []

            paths.startEditing()

            for feature_position, feature in enumerate(paths.getFeatures(), start=1):
                geometries.append(feature.geometry())

                if feature_position == position - 1:
                    geometries.append(Utils.create_polyline_geometry([(0, 0)]))

                paths.deleteFeature(feature.id())

            for geometry in geometries:
                feature = QgsFeature(paths.fields())
                feature.setGeometry(geometry)

                paths.addFeature(feature)

            paths.commitChanges()

            Segment.refesh_segment(paths, position - 1, a, b)
            Segment.refesh_segment(paths, position, b, c)

        # refresh last
        elif previous_point and current_point and not next_point:
            a = previous_point.geometry().asPoint()
            b = current_point.geometry().asPoint()

            paths.startEditing()

            feature = QgsFeature(paths.fields())
            feature.setGeometry(Utils.create_polyline_geometry([(0, 0)]))

            paths.addFeature(feature)
            paths.commitChanges()

            Segment.refesh_segment(paths, position - 1, a, b)

    @staticmethod
    def refresh_point_move(segment: QgsLayerTreeGroup, position: int):
        print(f'Segment::refresh_point_move(f{segment}, {position})')

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return

        previous_point = Segment.get_point(points, position - 1)
        current_point = Segment.get_point(points, position)
        next_point = Segment.get_point(points, position + 1)

        # refresh first
        if not previous_point and current_point and next_point:
            a = current_point.geometry().asPoint()
            b = next_point.geometry().asPoint()

            Segment.refesh_segment(paths, 1, a, b)

        # refresh middle
        elif previous_point and current_point and next_point:
            a = previous_point.geometry().asPoint()
            b = current_point.geometry().asPoint()
            c = next_point.geometry().asPoint()

            Segment.refesh_segment(paths, position - 1, a, b)
            Segment.refesh_segment(paths, position, b, c)

        # refresh last
        elif previous_point and current_point and not next_point:
            a = previous_point.geometry().asPoint()
            b = current_point.geometry().asPoint()

            Segment.refesh_segment(paths, position - 1, a, b)

    @staticmethod
    def refresh_point_delete(segment: QgsLayerTreeGroup, position: int):
        print(f'Segment::refresh_point_delete(f{segment}, {position})')

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return

        previous_point = Segment.get_point(points, position - 1)
        current_point = Segment.get_point(points, position)
        next_point = Segment.get_point(points, position + 1)

        # refresh first
        if position == 1:
            feature = Segment.get_path(paths, position)

            if feature:
                paths.startEditing()
                paths.deleteFeature(feature.id())
                paths.commitChanges()

        # refresh last
        elif position - 1 == points.featureCount():
            feature = Segment.get_path(paths, position - 1)

            if feature:
                paths.startEditing()
                paths.deleteFeature(feature.id())
                paths.commitChanges()

        # refresh middle
        elif previous_point and current_point:
            a = previous_point.geometry().asPoint()
            b = current_point.geometry().asPoint()

            feature = Segment.get_path(paths, position)

            if feature:
                paths.startEditing()
                paths.deleteFeature(feature.id())
                paths.commitChanges()

            Segment.refesh_segment(paths, position - 1, a, b)

    @staticmethod
    def refesh_segment(layer: QgsVectorLayer, position: int, a: QgsPointXY, b: QgsPointXY):
        print(f'Segment::refesh_segment({layer}, {position}, {a}, {b})')

        if Options.routing:
            results = Google.get_direction_as_points(f'{a.y()} {a.x()}', f'{b.y()} {b.x()}')

            if not results:
                return
        else:
            results = [a, b]

        feature = Segment.get_path(layer, position)

        if not feature:
            return

        layer.startEditing()
        layer.changeGeometry(feature.id(), Utils.create_polyline_geometry(results))
        layer.commitChanges()

    @staticmethod
    def get_point(layer: QgsVectorLayer, position: int) -> Optional[QgsFeature]:
        print(f'Segment::get_point(f{layer}, {position})')

        for feature_position, feature in enumerate(layer.getFeatures(), start=1):
            if feature_position == position:
                return feature

        return None

    @staticmethod
    def get_path(layer: QgsVectorLayer, position: int):
        print(f'Segment::get_path(f{layer}, {position})')

        for feature_position, feature in enumerate(layer.getFeatures(), start=1):
            if feature_position == position:
                return feature

        return None

    @staticmethod
    def from_xml(track: QgsLayerTreeGroup, trkseg: ET.Element):
        print(f'Segment::from_xml{track}, {trkseg})')

        segment = Segment.create(track)

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return

        results = []

        for trkpt in trkseg.iter('trkpt'):
            results.append((float(trkpt.get('lon')), float(trkpt.get('lat'))))

        if len(results) < 2:
            return

        points.startEditing()
        paths.startEditing()

        chunk_size = 30

        for i in range(math.ceil(len(results) / chunk_size)):
            chunk = results[i * chunk_size:(i + 1) * chunk_size]

            points.addFeature(Point.create_feature(QgsPoint(chunk[0][0], chunk[0][1]), points.fields()))
            paths.addFeature(Utils.create_polyline(chunk, paths.fields()))

        points.addFeature(Point.create_feature(QgsPoint(results[-1][0], results[-1][1]), points.fields()))

        points.commitChanges()
        paths.commitChanges()

        points.startEditing()
        Utils.refresh_position(points)
        points.commitChanges()

    @staticmethod
    def to_xml(segment: QgsLayerTreeGroup) -> Optional[ET.Element]:
        print(f'Segment::to_xml{segment})')

        if not segment:
            return None

        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return None

        trkseg = ET.Element('trkseg')

        for feature in paths.getFeatures():
            for part in feature.geometry().parts():
                for vertex in part.vertices():
                    ET.SubElement(trkseg, 'trkpt', lat=str(vertex.y()), lon=str(vertex.x()))

        return trkseg
