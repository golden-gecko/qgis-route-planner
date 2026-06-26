import datetime
import googlemaps
import math
import requests

from .config import Config
from .log import log_call
from .options import Options


class Google:
    Profiles = {
        'bicycle': 'bicycling',
        'car': 'driving',
        'foot': 'walking',
    }

    @staticmethod
    def get_avoid_options() -> list[str]:
        avoid = []

        if Options.avoid_highways:
            avoid.append('highways')

        if Options.avoid_tolls:
            avoid.append('tolls')

        return avoid

    @staticmethod
    @log_call
    def get_direction(a, b, mode: str = 'car') -> list:
        client = googlemaps.Client(key=Config.Google.Key)
        avoid = Google.get_avoid_options()

        return client.directions(
            a,
            b,
            mode=Google.Profiles.get(mode, 'driving'),
            avoid=avoid or None,
            departure_time=datetime.datetime.now()
        )

    @staticmethod
    @log_call
    def get_direction_as_points(a, b) -> list:
        result = Google.get_direction(a, b, Options.routing_mode)

        if len(result) <= 0:
            return []

        if 'overview_polyline' not in result[0]:
            return []

        if 'points' not in result[0]['overview_polyline']:
            return []

        point_str = str(result[0]['overview_polyline']['points'])

        coord_chunks = [[]]

        for char in point_str:
            value = ord(char) - 63
            split_after = not (value & 0x20)
            value &= 0x1F
            coord_chunks[-1].append(value)

            if split_after:
                coord_chunks.append([])

        del coord_chunks[-1]

        coords = []

        for coord_chunk in coord_chunks:
            coord = 0
            for i, chunk in enumerate(coord_chunk):
                coord |= chunk << (i * 5)

            if coord & 0x1:
                coord = ~coord

            coord >>= 1
            coord /= 100000.0
            coords.append(coord)

        points = []
        prev_x = 0
        prev_y = 0

        for i in range(0, len(coords) - 1, 2):
            if coords[i] == 0 and coords[i + 1] == 0:
                continue

            prev_x += coords[i + 1]
            prev_y += coords[i]
            points.append((round(prev_x, 6), round(prev_y, 6)))

        print(f'Google::get_direction_as_points({a}, {b}) - Got {len(points)} points')

        return points

    @staticmethod
    @log_call
    def get_nearby_panoramas(lat: float, lng: float, radius: int = 100, max_results: int = 10) -> list:
        results = {}

        def dest_point(lat0, lng0, distance_m, bearing_deg):
            R = 6378137.0
            brng = math.radians(bearing_deg)
            lat1 = math.radians(lat0)
            lon1 = math.radians(lng0)
            lat2 = math.asin(math.sin(lat1) * math.cos(distance_m / R) + math.cos(lat1) * math.sin(distance_m / R) * math.cos(brng))
            lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(distance_m / R) * math.cos(lat1), math.cos(distance_m / R) - math.sin(lat1) * math.sin(lat2))
            return math.degrees(lat2), math.degrees(lon2)

        # sampling distances and bearings (center + rings)
        distances = [0, radius / 2, radius]
        bearings = list(range(0, 360, 45))

        for d in distances:
            for b in bearings:
                if d == 0 and b != 0:
                    continue

                sample_lat, sample_lng = dest_point(lat, lng, d, b)

                resp = requests.get(
                    'https://maps.googleapis.com/maps/api/streetview/metadata',
                    params={
                        'location': f'{sample_lat},{sample_lng}',
                        'radius': radius,
                        'key': Config.Google.Key,
                    },
                    timeout=10,
                )
                data = resp.json()

                # metadata endpoint returns status 'OK' when panorama found
                status = data.get('status')
                if status != 'OK':
                    continue

                pano_id = data.get('pano_id') or data.get('panoId') or data.get('pano')
                loc = data.get('location') or {}
                lat_p = loc.get('lat')
                lng_p = loc.get('lng')

                if not pano_id:
                    # fallback: use location as identifier
                    pano_id = f"{lat_p}:{lng_p}"

                if pano_id not in results:
                    results[pano_id] = {
                        'pano_id': pano_id,
                        'lat': lat_p,
                        'lng': lng_p,
                        'date': data.get('date'),
                        'raw': data,
                    }

                if len(results) >= max_results:
                    break

            if len(results) >= max_results:
                break

        return list(results.values())
