def classFactory(iface):
    from .route_planner import RoutePlanner
    return RoutePlanner(iface)
