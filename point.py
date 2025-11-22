from .map_tools import PointAdd, PointDelete, PointMove


class Point:
    @staticmethod
    def add(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointAdd(iface, canvas))

    @staticmethod
    def delete(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointDelete(iface, canvas))

    @staticmethod
    def move(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointMove(iface, canvas))
