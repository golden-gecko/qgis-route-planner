import json
import urllib.parse
import urllib.request

from .config import Config
from .log import log_call
from .options import Options


class OpenRouteService:
    PROFILES = {
        'driving': 'driving-car',
        'walking': 'foot-walking',
        'bicycling': 'cycling-regular',
    }

    @staticmethod
    def _parse_point(point) -> tuple[float, float]:
        if isinstance(point, str):
            lat, lon = point.split()
            return float(lon), float(lat)

        return float(point[0]), float(point[1])

    @staticmethod
    def get_avoid_features() -> list[str]:
        features = []

        if Options.avoid_highways:
            features.append('highways')

        if Options.avoid_tolls:
            features.append('tollways')

        return features

    @staticmethod
    @log_call
    def get_direction(a, b, mode: str = 'driving') -> dict:
        profile = OpenRouteService.PROFILES.get(mode, 'driving-car')
        start = OpenRouteService._parse_point(a)
        end = OpenRouteService._parse_point(b)

        payload = {
            'coordinates': [
                [start[0], start[1]],
                [end[0], end[1]],
            ],
            'geometry_simplify': False,
        }

        avoid_features = OpenRouteService.get_avoid_features()

        if avoid_features:
            payload['options'] = {
                'avoid_features': avoid_features
            }

        url = (
            f'https://api.openrouteservice.org/v2/directions/{profile}/geojson'
            f'?{urllib.parse.urlencode({"api_key": Config.OpenRouteService.Key})}'
        )
        data = json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            method='POST'
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))

    @staticmethod
    @log_call
    def get_direction_as_points(a, b) -> list:
        result = OpenRouteService.get_direction(a, b, Options.routing_mode)
        features = result.get('features', [])

        if not features:
            return []

        coordinates = features[0].get('geometry', {}).get('coordinates', [])

        return [
            (round(float(lon), 6), round(float(lat), 6))
            for lon, lat in coordinates
        ]
