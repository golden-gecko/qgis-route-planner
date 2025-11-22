from .map_tools import PointCreateEnd, PointCreateStart, PointDelete, PointMove


class Point:
    @staticmethod
    def create_start(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointCreateStart(iface, canvas))

    @staticmethod
    def create_end(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointCreateEnd(iface, canvas))

    @staticmethod
    def delete(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointDelete(iface, canvas))

    @staticmethod
    def move(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointMove(iface, canvas))
