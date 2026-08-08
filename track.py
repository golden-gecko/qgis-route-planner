import gpxpy

from typing import Optional

from qgis.core import QgsLayerTree, QgsLayerTreeGroup

from .dialog import Dialog
from .log import log_call
from .segment import Segment
from .string import String
from .tree import Tree


class Track:
    @staticmethod
    @log_call
    def create(file: Optional[QgsLayerTreeGroup], name: Optional[str] = None) -> Optional[QgsLayerTreeGroup]:
        tracks = Tree.find_group(file, 'Tracks')

        if not tracks:
            return None

        if not name:
            name = String.generate_name('Track', len(tracks.children()))

        track = Tree.create_group(tracks, name)

        if track is None:
            return None

        track.setCustomProperty('type', 'track')

        return track

        # TODO: Try to use data sources.
        # DataSource.set(point_layer, file_name + '?type=waypoint')
        # DataSource.set(path_layer, file_name + '?type=track')

        # TODO: Must be called after setting data source.
        # point_layer.setLabeling(Label.create_settings())

    @staticmethod
    @log_call
    def delete(track: Optional[QgsLayerTreeGroup]):
        if track is None:
            return

        if Dialog.confirm('Delete track?'):
            Tree.delete_group(track)

    @staticmethod
    @log_call
    def get_active(iface) -> Optional[QgsLayerTreeGroup]:
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
    @log_call
    def refresh(track: Optional[QgsLayerTreeGroup]):
        if track is None:
            return

        for segment in track.children():
            if segment.customProperty('type') == 'segment':
                Segment.refresh(segment)

    @staticmethod
    @log_call
    def reverse(track: Optional[QgsLayerTreeGroup]):
        if track is None:
            return

        for segment in track.children():
            if segment.customProperty('type') == 'segment':
                Segment.reverse(segment)

    @staticmethod
    @log_call
    def optimize(track: Optional[QgsLayerTreeGroup]):
        if track is None:
            return

        for segment in track.children():
            if segment.customProperty('type') == 'segment':
                Segment.optimize(segment)

    @staticmethod
    @log_call
    def from_gpx(file: Optional[QgsLayerTreeGroup], gpx_track: gpxpy.gpx.GPXTrack):
        """Import a gpxpy GPXTrack into the project as a Track group."""
        name = getattr(gpx_track, 'name', None)

        track = Track.create(file, name)

        if track is None:
            return

        for seg in gpx_track.segments:
            results = []
            for pt in seg.points:
                lat = getattr(pt, 'latitude', None)
                lon = getattr(pt, 'longitude', None)
                if lat is None or lon is None:
                    continue
                results.append((float(lon), float(lat)))

            if results:
                Segment.from_points(track, results)

    @staticmethod
    @log_call
    def to_gpx_track(track: Optional[QgsLayerTreeGroup]) -> gpxpy.gpx.GPXTrack:
        if track is None:
            return None

        gpx_track = gpxpy.gpx.GPXTrack(name=track.name())

        for segment in track.children():
            if segment.customProperty('type') != 'segment':
                continue

            gpx_segment = Segment.to_gpx_segment(segment)

            if not gpx_segment:
                continue

            gpx_track.segments.append(gpx_segment)

        return gpx_track

    @staticmethod
    @log_call
    def get_distance(track: Optional[QgsLayerTreeGroup]) -> float:
        if track is None:
            return 0.0

        distance = 0.0

        for segment in track.children():
            distance += Segment.get_distance(segment)

        return distance
