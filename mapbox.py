import json
import urllib.parse
import urllib.request

from .config import Config
from .log import log_call
from .options import Options


class MapBox:
    PROFILES = {
        'driving': 'mapbox/driving',
        'walking': 'mapbox/walking',
        'bicycling': 'mapbox/cycling',
    }

    @staticmethod
    def _parse_point(point) -> tuple[float, float]:
        if isinstance(point, str):
            lat, lon = point.split()
            return float(lon), float(lat)

        return float(point[0]), float(point[1])

    @staticmethod
    def get_exclude_options() -> list[str]:
        exclude = []

        if Options.avoid_highways:
            exclude.append('motorway')

        if Options.avoid_tolls:
            exclude.append('toll')

        return exclude

    @staticmethod
    @log_call
    def get_direction(a, b, mode: str = 'driving') -> dict:
        profile = MapBox.PROFILES.get(mode, 'mapbox/driving')
        start = MapBox._parse_point(a)
        end = MapBox._parse_point(b)
        coords = f'{start[0]},{start[1]};{end[0]},{end[1]}'

        params = {
            'access_token': Config.MapBox.Key,
            'geometries': 'geojson',
            'overview': 'full',
        }

        exclude = MapBox.get_exclude_options()

        if exclude:
            params['exclude'] = ','.join(exclude)

        url = (
            f'https://api.mapbox.com/directions/v5/{profile}/{coords}'
            f'?{urllib.parse.urlencode(params)}'
        )

        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))

    @staticmethod
    @log_call
    def get_direction_as_points(a, b) -> list:
        result = MapBox.get_direction(a, b, Options.routing_mode)
        routes = result.get('routes', [])

        if not routes:
            return []

        geometry = routes[0].get('geometry', {})
        coordinates = geometry.get('coordinates', [])

        return [
            (round(float(lon), 6), round(float(lat), 6))
            for lon, lat in coordinates
        ]
