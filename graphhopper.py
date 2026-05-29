import json
import urllib.parse
import urllib.request

from .config import Config
from .log import log_call
from .options import Options


class GraphHopper:
    Profiles = {
        'bicycle': 'bike',
        'car': 'car',
        'foot': 'foot',
    }

    @staticmethod
    def _parse_point(point) -> tuple[float, float]:
        if isinstance(point, str):
            lat, lon = point.split()
            return float(lon), float(lat)

        return float(point[0]), float(point[1])

    @staticmethod
    def get_avoid_options() -> list[str]:
        avoid = []

        if Options.avoid_highways:
            avoid.append('motorway')

        if Options.avoid_tolls:
            avoid.append('toll')

        return avoid

    @staticmethod
    @log_call
    def get_direction(a, b, mode: str = 'car') -> dict:
        start = GraphHopper._parse_point(a)
        end = GraphHopper._parse_point(b)

        params = [
            ('point', f'{start[1]},{start[0]}'),
            ('point', f'{end[1]},{end[0]}'),
            ('profile', GraphHopper.Profiles.get(mode, 'car')),
            ('points_encoded', 'false'),
            ('key', Config.GraphHopper.Key),
        ]

        avoid = GraphHopper.get_avoid_options()

        if avoid:
            params.append(('ch.disable', 'true'))
            params.append(('avoid', ','.join(avoid)))

        url = (
            'https://graphhopper.com/api/1/route'
            f'?{urllib.parse.urlencode(params)}'
        )

        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))

    @staticmethod
    @log_call
    def get_direction_as_points(a, b) -> list:
        result = GraphHopper.get_direction(a, b, Options.routing_mode)
        paths = result.get('paths', [])

        if not paths:
            return []

        coordinates = paths[0].get('points', {}).get('coordinates', [])

        return [
            (round(float(lon), 6), round(float(lat), 6))
            for lon, lat in coordinates
        ]
