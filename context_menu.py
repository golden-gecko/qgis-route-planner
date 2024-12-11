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

        point = event.mapPoint()
        point = Utils.transform_crs(QgsGeometry.fromPointXY(point), 3857, 4326).asPoint()

        sub_menu = menu.addMenu('My Menu')

        action = sub_menu.addAction('Create at start')
        action.triggered.connect(lambda: ContextMenu.create_at_start(point))

        action = sub_menu.addAction('Create in the middle')
        action.triggered.connect(lambda: ContextMenu.create_in_the_middle(point))

        action = sub_menu.addAction('Create at end')
        action.triggered.connect(lambda: ContextMenu.create_at_end(point))

    @staticmethod
    def create_at_start(point):
        print(f'ContextMenu::create_at_start({point})')

        track = Track.get_active(get_iface())
        layer = Utils.get_or_create_point_layer(track)

        feature = QgsFeature(layer.fields())
        feature.setGeometry(QgsGeometry.fromPointXY(point))

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()

    @staticmethod
    def create_in_the_middle(point):
        print(f'ContextMenu::create_in_the_middle({point})')

    @staticmethod
    def create_at_end(point):
        print(f'ContextMenu::create_at_end({point})')
