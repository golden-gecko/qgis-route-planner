from qgis.core import QgsGeometry, QgsWkbTypes
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent

from qgis.PyQt.QtWidgets import QMenu

from .iface import Iface
from .point import Point
from .track import Track
from .utils import Utils

class ContextMenu:
    sub_menu = None

    @staticmethod
    def create(canvas: QgsMapCanvas):
        print('ContextMenu::create()')

        canvas.contextMenuAboutToShow.connect(ContextMenu.populate)

    @staticmethod
    def populate(menu: QMenu, event: QgsMapMouseEvent):
        print(f'ContextMenu::populate({menu}, {event})')

        point = event.mapPoint()
        point = Utils.transform_crs(QgsGeometry.fromPointXY(point), 3857, 4326).asPoint()

        ContextMenu.sub_menu = menu.addMenu('My Menu')

        action = ContextMenu.sub_menu.addAction('Create at start')
        action.triggered.connect(lambda: ContextMenu.create_at_start(point))

        action = ContextMenu.sub_menu.addAction('Create in the middle')
        action.triggered.connect(lambda: ContextMenu.create_in_the_middle(point))

        action = ContextMenu.sub_menu.addAction('Create at end')
        action.triggered.connect(lambda: ContextMenu.create_at_end(point))

    @staticmethod
    def create_at_start(point):
        print(f'ContextMenu::create_at_start({point})')

        track = Track.get_active(Iface.get())
        layer = Track.get_or_create_point_layer(track)

        Point.create_start(layer, point)
        Track.refresh_point_create_start(track, 1)

    @staticmethod
    def create_in_the_middle(point):
        print(f'ContextMenu::create_in_the_middle({point})')

        track = Track.get_active(Iface.get())
        layer = Track.get_or_create_point_layer(track)
        buffer = Utils.create_buffer(point)

        position = 1

        for feature in Track.get_or_create_path_layer(track).getFeatures():
            if feature.geometry().type() == QgsWkbTypes.LineGeometry:
                if feature.geometry().intersects(buffer):
                    Point.create_middle(layer, point, position + 1)
                    Track.refresh_point_create_middle(track, position + 1)

                    break

            position += 1

    @staticmethod
    def create_at_end(point):
        print(f'ContextMenu::create_at_end({point})')

        track = Track.get_active(Iface.get())
        layer = Track.get_or_create_point_layer(track)

        Point.create_end(layer, point)
        Track.refresh_point_create_end(track, layer.featureCount())
