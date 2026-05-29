class Options:
    routing = True
    routing_provider = 'Google'
    routing_mode = 'driving'

    avoid_highways = False
    avoid_tolls = False

    control_point_per_segment = 100
    control_point_min_distance = 1000
    control_point_min_angle = 20

    @staticmethod
    def set_routing(routing: bool) -> None:
        Options.routing = routing

    @staticmethod
    def set_routing_provider(routing_provider: str) -> None:
        if routing_provider not in ['Google', 'GraphHopper', 'MapBox', 'OpenRouteService']:
            routing_provider = 'Google'

        Options.routing_provider = routing_provider

    @staticmethod
    def set_routing_mode(routing_mode: str) -> None:
        if routing_mode not in ['bicycling', 'driving', 'walking']:
            routing_mode = 'driving'

        Options.routing_mode = routing_mode

    @staticmethod
    def set_avoid_highways(avoid_highways: bool) -> None:
        Options.avoid_highways = avoid_highways

    @staticmethod
    def set_avoid_tolls(avoid_tolls: bool) -> None:
        Options.avoid_tolls = avoid_tolls

    @staticmethod
    def set_control_point_per_segment(control_point_per_segment: int) -> None:
        Options.control_point_per_segment = max(2, min(control_point_per_segment, 100))

    @staticmethod
    def set_control_point_min_distance(control_point_min_distance: int) -> None:
        Options.control_point_min_distance = max(1, min(control_point_min_distance, 1000))

    @staticmethod
    def set_control_point_min_angle(control_point_min_angle: int) -> None:
        Options.control_point_min_angle = max(1, min(control_point_min_angle, 180))
