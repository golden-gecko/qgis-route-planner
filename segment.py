import math
import xml.etree.ElementTree as ET

from typing import Optional

from qgis.core import QgsFeature, QgsLayerTree, QgsLayerTreeGroup, QgsPoint, QgsPointXY, QgsVectorLayer

from .feature import Feature
from .log import log_call
from .color import Color
from .google import Google
from .layer import Layer
from .options import Options
from .symbol import Symbol
from .tree import Tree
from .utils import Utils


class Segment:
    @staticmethod
    @log_call
    def create(track: QgsLayerTreeGroup) -> Optional[QgsLayerTreeGroup]:

        if not track:
            return None

        segment = Tree.create_group(track, Utils.generate_name('Segment', len(track.children())), 'segment')

        if not segment:
            return None

        points = Layer.get_or_create_points(segment)
        paths = Layer.get_or_create_paths(segment)

        color = Color.random()

        Utils.set_symbol(points, Symbol.create_point(color))
        Utils.set_symbol(paths, Symbol.create_path(color))

        return segment

    @staticmethod
    @log_call
    def refresh(segment: QgsLayerTreeGroup):

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
    @log_call
    def refresh_points(segment: QgsLayerTreeGroup):

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return

        points.startEditing()
        paths.startEditing()

        results = []

        for path in paths.getFeatures():
            for part in path.geometry().parts():
                for vertex in part.vertices():
                    results.append((vertex.x(), vertex.y()))

        for feature in points.getFeatures():
            points.deleteFeature(feature.id())

        for feature in paths.getFeatures():
            paths.deleteFeature(feature.id())

        chunk_size = math.ceil(len(results) / (Options.points_per_segment - 1))

        for i in range(math.ceil(len(results) / chunk_size)):
            chunk = results[i * chunk_size:(i + 1) * chunk_size]

            points.addFeature(Feature.from_point(QgsPoint(chunk[0][0], chunk[0][1]), points.fields()))
            paths.addFeature(Utils.create_polyline(chunk, paths.fields()))

        points.addFeature(Feature.from_point(QgsPoint(results[-1][0], results[-1][1]), points.fields()))

        points.commitChanges()
        paths.commitChanges()

        points.startEditing()
        Utils.refresh_position(points)
        points.commitChanges()

    @staticmethod
    @log_call
    def reverse(segment: QgsLayerTreeGroup):

        if not segment:
            return

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return

        points_list = []
        paths_list = []

        for feature in points.getFeatures():
            points_list.append((feature.geometry().asPoint().x(), feature.geometry().asPoint().y()))

        for feature in paths.getFeatures():
            lines = []

            for part in feature.geometry().parts():
                for vertex in part.vertices():
                    lines.append((vertex.x(), vertex.y()))

            paths_list.append(lines)

        points.startEditing()
        paths.startEditing()

        for feature in points.getFeatures():
            points.deleteFeature(feature.id())

        for feature in paths.getFeatures():
            paths.deleteFeature(feature.id())

        points_list.reverse()

        for point in points_list:
            points.addFeature(Feature.from_point(QgsPoint(point[0], point[1]), points.fields()))

        for path in paths_list:
            path.reverse()

        paths_list.reverse()

        for i in paths_list:
            paths.addFeature(Utils.create_polyline(i, paths.fields()))

        points.commitChanges()
        paths.commitChanges()

        points.startEditing()
        Utils.refresh_position(points)
        points.commitChanges()

    @staticmethod
    @log_call
    def optimize(segment: QgsLayerTreeGroup):

        if not segment:
            return

    @staticmethod
    @log_call
    def delete(segment: QgsLayerTreeGroup):

        if not segment:
            return

        if Utils.confirm('Delete segment?'):
            Tree.delete_group(segment)

    @staticmethod
    @log_call
    def get_active(iface) -> Optional[QgsLayerTreeGroup]:

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
    @log_call
    def refresh_point(segment: QgsLayerTreeGroup, position: int):

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
    @log_call
    def refresh_point_move(segment: QgsLayerTreeGroup, position: int):

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
    @log_call
    def refresh_point_delete(segment: QgsLayerTreeGroup, position: int):

        points = Layer.get_or_create_points(segment)

        if not points:
            return

        paths = Layer.get_or_create_paths(segment)

        if not paths:
            return

        previous_point = Segment.get_point(points, position - 1)
        current_point = Segment.get_point(points, position)

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
    @log_call
    def refesh_segment(layer: QgsVectorLayer, position: int, a: QgsPointXY, b: QgsPointXY):

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
    @log_call
    def get_point(layer: QgsVectorLayer, position: int) -> Optional[QgsFeature]:

        for feature_position, feature in enumerate(layer.getFeatures(), start=1):
            if feature_position == position:
                return feature

        return None

    @staticmethod
    @log_call
    def get_path(layer: QgsVectorLayer, position: int):

        for feature_position, feature in enumerate(layer.getFeatures(), start=1):
            if feature_position == position:
                return feature

        return None

    @staticmethod
    @log_call
    def from_xml(track: QgsLayerTreeGroup, trkseg: ET.Element):

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

        chunk_size = math.ceil(len(results) / (Options.points_per_segment - 1))

        for i in range(math.ceil(len(results) / chunk_size)):
            chunk = results[i * chunk_size:(i + 1) * chunk_size]

            points.addFeature(Feature.from_point(QgsPoint(chunk[0][0], chunk[0][1]), points.fields()))
            paths.addFeature(Utils.create_polyline(chunk, paths.fields()))

        points.addFeature(Feature.from_point(QgsPoint(results[-1][0], results[-1][1]), points.fields()))

        points.commitChanges()
        paths.commitChanges()

        points.startEditing()
        Utils.refresh_position(points)
        points.commitChanges()

    @staticmethod
    @log_call
    def to_xml(segment: QgsLayerTreeGroup) -> Optional[ET.Element]:

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

    @staticmethod
    @log_call
    def get_distance(segment: QgsLayerTreeGroup) -> float:

        if not segment:
            return 0.0

        return Utils.get_distance(Layer.get_or_create_paths(segment))
