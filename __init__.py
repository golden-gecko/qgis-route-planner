from .route_planner import RoutePlanner


def classFactory(iface):
    return RoutePlanner(iface)
