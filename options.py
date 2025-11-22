class Options:
    routing = True
    routing_provider = 'Google'

    @staticmethod
    def set_routing(routing: bool):
        Options.routing = routing

    @staticmethod
    def set_routing_provider(routing_provider: str):
        Options.routing_provider = routing_provider
