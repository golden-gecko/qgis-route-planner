import re
import os
import gpxpy

from typing import Optional

from qgis.core import QgsLayerTree, QgsLayerTreeGroup, QgsPointXY

from .color import Color
from .dialog import Dialog
from .log import log_call
from .layer import Layer
from .string import String
from .segment import Segment
from .symbol import Symbol
from .track import Track
from .tree import Tree
from .utils import Utils
from .waypoint import Waypoint


class File:
    @staticmethod
    @log_call
    def new(name: Optional[str] = None) -> Optional[QgsLayerTreeGroup]:
        files = Tree.get_or_create_group(Tree.get_root(), 'Tracks')

        if files is None:
            return None

        if name is None:
            name = String.generate_name('File', len(files.children()))

        file = Tree.create_group(files, name, 'file')

        if file is None:
            return None

        waypoints = Tree.create_group(file, 'Waypoints', 'waypoints')

        if waypoints is None:
            return None

        points = Layer.get_or_create_waypoints(waypoints)

        if points is None:
            return None

        Symbol.set(points, Symbol.create_waypoint(Color.random()))

        tracks = Tree.create_group(file, 'Tracks', 'tracks')

        if tracks is None:
            return None

        return file

    @staticmethod
    @log_call
    def open():
        file_name = Dialog.get_file_name()

        if file_name is None:
            return

        File.load_xml(file_name)

    @staticmethod
    @log_call
    def save(file: Optional[QgsLayerTreeGroup], extension_osmand:bool = True):
        if file is None:
            return

        file_name = file.customProperty('fileName')

        if not file_name:
            file_name = Dialog.get_file_name()

            if not file_name:
                return

            file.setName(os.path.basename(file_name))
            file.setCustomProperty('fileName', file_name)

            File.refresh_distance(file)

        waypoints = Tree.find_group(file, 'Waypoints')

        if not waypoints:
            return

        # Build GPX using gpxpy
        gpx = gpxpy.gpx.GPX()

        # waypoints
        points_layer = Layer.get_or_create_waypoints(waypoints)
        if points_layer is not None:
            for feature in points_layer.getFeatures():
                geom = feature.geometry().asPoint()
                name = feature.attribute('name')
                wpt = gpxpy.gpx.GPXWaypoint(latitude=geom.y(), longitude=geom.x(), name=name)
                gpx.waypoints.append(wpt)

        tracks = Tree.find_group(file, 'Tracks')

        if not tracks:
            # write gpx even if there are no tracks
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(gpx.to_xml())
            return

        for track in tracks.children():
            if track.customProperty('type') != 'track':
                continue

            gpx_track = gpxpy.gpx.GPXTrack(name=track.name())

            for segment in track.children():
                if segment.customProperty('type') != 'segment':
                    continue

                gpx_segment = gpxpy.gpx.GPXTrackSegment()

                paths = Layer.get_or_create_paths(segment)
                if paths is None:
                    continue

                for feature in paths.getFeatures():
                    for part in feature.geometry().parts():
                        for vertex in part.vertices():
                            pt = gpxpy.gpx.GPXTrackPoint(latitude=vertex.y(), longitude=vertex.x())
                            gpx_segment.points.append(pt)

                gpx_track.segments.append(gpx_segment)

            gpx.tracks.append(gpx_track)

        # serialize GPX to file
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(gpx.to_xml())

    @staticmethod
    @log_call
    def close(file: Optional[QgsLayerTreeGroup], force: bool = False):
        if file is None:
            return

        if force or Dialog.confirm('Close file?'):
            Tree.delete_group(file)

    @staticmethod
    @log_call
    def get_active(iface) -> Optional[QgsLayerTreeGroup]:
        nodes = iface.layerTreeView().selectedNodes()

        if len(nodes) != 1:
            return None

        node = nodes[0]

        while node.parent() and type(node.parent()) != QgsLayerTree:
            node_type = node.customProperty('type')

            if node_type and node_type == 'file':
                return node

            node = node.parent()

        return None

    @staticmethod
    @log_call
    def refresh_distance(file: Optional[QgsLayerTreeGroup]):
        if file is None:
            return

        files = Tree.get_or_create_group(Tree.get_root(), 'Tracks')

        if not files:
            return

        file_name = file.customProperty('fileName')

        if file_name:
            file.setName(f'{os.path.basename(file_name)} [{File.get_distance(file):.2f} km]')
        else:
            file.setName(f'File {len(files.children())} [{File.get_distance(file):.2f} km]')

        tracks = Tree.find_group(file, 'Tracks')

        if tracks:
            for track in tracks.children():
                if track.customProperty('type') != 'track':
                    continue

                Utils.update_distance(track, Track.get_distance(track))

                for segment in track.children():
                    if segment.customProperty('type') != 'segment':
                        continue

                    Utils.update_distance(segment, Segment.get_distance(segment))

    @staticmethod
    @log_call
    def reload(file: Optional[QgsLayerTreeGroup]):
        if file is None:
            return

        file_name = file.customProperty('fileName')

        if file_name is None:
            return

        File.close(file, True)
        File.load_xml(file_name)

    @staticmethod
    def load_xml(file_name: str):
        # load file contents and parse GPX with gpxpy
        with open(file_name, 'r', encoding='utf-8') as f:
            xml_string = f.read()

        gpx = gpxpy.parse(xml_string)

        # create file
        file = File.new(os.path.basename(file_name))

        if file is None:
            return

        file.setCustomProperty('fileName', file_name)

        waypoints_group = Tree.find_group(file, 'Waypoints')

        if not waypoints_group:
            return

        points = Layer.get_or_create_waypoints(waypoints_group)

        # import waypoints
        for wpt in gpx.waypoints:
            name = getattr(wpt, 'name', None)
            lat = getattr(wpt, 'latitude', None)
            lon = getattr(wpt, 'longitude', None)
            if lat is None or lon is None:
                continue
            Waypoint.create(points, QgsPointXY(lon, lat), name)

        # import tracks using Segment.from_points
        for gpx_track in gpx.tracks:
            # create a track group
            track_group = Track.create(file, getattr(gpx_track, 'name', None))
            if track_group is None:
                continue

            for seg in gpx_track.segments:
                results = []
                for pt in seg.points:
                    lat = getattr(pt, 'latitude', None)
                    lon = getattr(pt, 'longitude', None)
                    if lat is None or lon is None:
                        continue
                    results.append((float(lon), float(lat)))

                if results:
                    Segment.from_points(track_group, results)

        File.refresh_distance(file)

    @staticmethod
    @log_call
    def get_distance(file: Optional[QgsLayerTreeGroup]) -> float:
        if file is None:
            return 0.0

        tracks = Tree.find_group(file, 'Tracks')

        if not tracks:
            return 0.0

        distance = 0.0

        for track in tracks.children():
            if track.customProperty('type') != 'track':
                continue

            distance += Track.get_distance(track)

        return distance
