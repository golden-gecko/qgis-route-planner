from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFeature, QgsGeometry, QgsPoint, QgsProject
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent

from qgis.PyQt.QtWidgets import QMenu

from .iface import get_iface
from .track import Track
from .utils import Utils

class ContextMenu:
    @staticmethod
    def create(canvas: QgsMapCanvas):
        print('ContextMenu::create()')

        canvas.contextMenuAboutToShow.connect(ContextMenu.populate)

    @staticmethod
    def populate(menu: QMenu, event: QgsMapMouseEvent):
        print(f'ContextMenu::populate({menu}, {event})')

        sub_menu = menu.addMenu('My Menu')

        action = sub_menu.addAction('Create at start')
        action.triggered.connect(lambda: ContextMenu.create_at_start(event.mapPoint()))

        action = sub_menu.addAction('Create in the middle')
        action.triggered.connect(lambda: ContextMenu.create_in_the_middle(event.mapPoint()))

        action = sub_menu.addAction('Create at end')
        action.triggered.connect(lambda: ContextMenu.create_at_end(event.mapPoint()))

    @staticmethod
    def create_at_start(map_point):
        print(f'ContextMenu::action({map_point})')

        track = Track.get_active(get_iface())
        layer = Utils.get_or_create_point_layer(track)

        feature = QgsFeature(layer.fields())
        feature.setGeometry(QgsGeometry.fromPointXY(map_point))

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()

    @staticmethod
    def create_in_the_middle(map_point):
        pass

    @staticmethod
    def create_at_end(map_point):
        pass
