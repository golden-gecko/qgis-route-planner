class Options:
    routing = True
    routing_provider = 'Google'
    routing_mode = 'driving'

    @staticmethod
    def set_routing(routing: bool):
        Options.routing = routing

    @staticmethod
    def set_routing_provider(routing_provider: str):
        Options.routing_provider = routing_provider

    @staticmethod
    def set_routing_mode(routing_mode: str):
        Options.routing_mode = routing_mode
