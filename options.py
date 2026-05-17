class Options:
    routing = True
    routing_provider = 'Google'
    routing_mode = 'driving'
    points_per_segment = 30
    min_point_distance = 50.0

    @staticmethod
    def set_routing(routing: bool):
        Options.routing = routing

    @staticmethod
    def set_routing_provider(routing_provider: str):
        if routing_provider != 'Google':
            routing_provider = 'Google'

        Options.routing_provider = routing_provider

    @staticmethod
    def set_routing_mode(routing_mode: str):
        if routing_mode not in ['driving', 'walking']:
            routing_mode = 'driving'

        Options.routing_mode = routing_mode

    @staticmethod
    def set_points_per_segment(points_per_segment: int):
        if points_per_segment < 2:
            points_per_segment = 2

        Options.points_per_segment = points_per_segment
