class Options:
    routing = True
    routing_provider = 'Google'
    routing_mode = 'driving'
    points_per_segment = 100
    min_point_distance = 1000

    @staticmethod
    def set_routing(routing: bool) -> None:
        Options.routing = routing

    @staticmethod
    def set_routing_provider(routing_provider: str) -> None:
        if routing_provider != 'Google':
            routing_provider = 'Google'

        Options.routing_provider = routing_provider

    @staticmethod
    def set_routing_mode(routing_mode: str) -> None:
        if routing_mode not in ['driving', 'walking']:
            routing_mode = 'driving'

        Options.routing_mode = routing_mode

    @staticmethod
    def set_points_per_segment(points_per_segment: int) -> None:
        Options.points_per_segment = max(2, min(points_per_segment, 100))

    @staticmethod
    def set_min_point_distance(min_point_distance: int) -> None:
        Options.min_point_distance = max(1, min(min_point_distance, 1000))
