import datetime

import googlemaps


class Google:
    @staticmethod
    def get_direction(a, b) -> list:
        print(f'Google::get_direction({a}, {b})')

        client = googlemaps.Client(key='AIzaSyBw1mZbt__9-Ch863hR5K6c9_SPbZqIKrE')

        return client.directions(a, b, mode='driving', departure_time=datetime.datetime.now())

    @staticmethod
    def get_direction_as_points(a, b) -> list:
        print(f'Google::get_direction_as_points({a}, {b})')

        result = Google.get_direction(a, b)

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
