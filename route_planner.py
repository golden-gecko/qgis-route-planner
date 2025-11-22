import os.path

from qgis.core import QgsDistanceArea, QgsGeometry, QgsLayerTreeGroup, QgsLineSymbol, QgsPoint, QgsVectorLayer, QgsWkbTypes
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction

from .google import Google
from .map_tools import PointAdd, PointDelete, PointMove
from .route_planner_dockwidget import RoutePlannerDockWidget
from .utils import Utils

from .resources import *


class RoutePlanner:
    def __init__(self, iface):
        print('RoutePlanner::__init__()')

        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        self.actions = []
        self.menu = '&RoutePlanner'
        self.toolbar = self.iface.addToolBar('RoutePlanner')
        self.toolbar.setObjectName('RoutePlanner')

        self.pluginIsActive = False
        self.dockwidget = None


    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        print('RoutePlanner::add_action()')

        action = QAction(QIcon(icon_path), text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

    def initGui(self):
        print('RoutePlanner::initGui()')

        self.add_action(':/plugins/route_planner/icon.png', text='Show', callback=self.run, parent=self.iface.mainWindow())

        self.subscribe_to_layers()

    def onClosePlugin(self):
        print('RoutePlanner::onClosePlugin()')

        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.pluginIsActive = False

    def unload(self):
        print('RoutePlanner::unload()')

        for action in self.actions:
            self.iface.removePluginMenu('&RoutePlanner', action)
            self.iface.removeToolBarIcon(action)

        del self.toolbar

    def run(self):
        print('RoutePlanner::run()')

        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.dockwidget is None:
                self.dockwidget = RoutePlannerDockWidget()

            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            self.dockwidget.buttonTrackAdd.clicked.connect(self.track_add)
            self.dockwidget.buttonTrackDelete.clicked.connect(self.track_delete)
            self.dockwidget.buttonTrackRefresh.clicked.connect(self.track_refresh)

            self.dockwidget.buttonPointAdd.clicked.connect(self.point_add)
            self.dockwidget.buttonPointDelete.clicked.connect(self.point_delete)
            self.dockwidget.buttonPointMove.clicked.connect(self.point_move)

            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    def track_add(self):
        print('RoutePlanner::track_add()')

        tracks = Utils.get_or_create_tracks_directory()

        if not tracks:
            return

        track = Utils.create_track_directory(tracks, Utils.generate_track_name(tracks))

        if not track:
            return

        Utils.get_or_create_point_layer(track)
        Utils.get_or_create_path_layer(track)

    def track_delete(self):
        print('RoutePlanner::track_delete()')

        tracks = Utils.get_or_create_tracks_directory()

        if not tracks:
            return

        track = self.get_active_track()

        if not track:
            return

        tracks.removeChildNode(track)

    def track_refresh(self):
        print('RoutePlanner::track_refresh()')

        track = self.get_active_track()

        if not track:
            return

        point_layer = Utils.get_or_create_point_layer(track)

        if not point_layer:
            return

        path_layer = Utils.get_or_create_path_layer(track)

        if not path_layer:
            return

        points = []

        for feature in point_layer.getFeatures():
            if feature.geometry().type() == QgsWkbTypes.PointGeometry:
                points.append((feature.geometry().asPoint().x(), feature.geometry().asPoint().y()))

        if not points:
            return

        path = []

        for i in range(len(points) - 1):
            path_points = Google.get_direction_as_points(f'{points[i][1]} {points[i][0]}', f'{points[i + 1][1]} {points[i + 1][0]}')

            if not path_points:
                continue

            print(f'RoutePlanner::track_refresh() - Got {len(path_points)} points')

            path.append(path_points)

        self.update_layer(point_layer, path_layer, path)

    def point_add(self):
        canvas = self.iface.mapCanvas()
        canvas.setMapTool(PointAdd(canvas, Utils.get_or_create_point_layer(self.get_active_track())))

    def point_delete(self):
        canvas = self.iface.mapCanvas()
        canvas.setMapTool(PointDelete(canvas, Utils.get_or_create_point_layer(self.get_active_track())))

    def point_move(self):
        canvas = self.iface.mapCanvas()
        canvas.setMapTool(PointMove(canvas, Utils.get_or_create_point_layer(self.get_active_track())))

    """
    def route_edit(self):
        print('RoutePlanner::route_edit()')

        if self.dockwidget.buttonTrackEdit.isChecked():
            self.set_mode_edit()
        else:
            self.set_mode_select()

    def set_mode_edit(self):
        print('RoutePlanner::set_mode_edit()')

        self.mode = Mode.Edit

        canvas = self.iface.mapCanvas()
        canvas.setMapTool(TrackEditTool(canvas, self.get_active_track()))

    def set_mode_select(self):
        print('RoutePlanner::set_mode_select()')

        self.mode = Mode.Select

        # TODO: Does not work.
        # canvas = self.iface.mapCanvas()
        # canvas.setMapTool(QgsMapToolPan(canvas))
    """

    def update_layer(self, points_layer: QgsVectorLayer, path_layer, path):
        print(f'RoutePlanner::update_layer() - Updating layer {Utils.get_parent_name(path_layer)}')

        self.remove_non_point_geometries(points_layer)

        vl = path_layer
        pr = vl.dataProvider()
        vl.startEditing()
        vl.renderer().symbol(). setColor(QColor('red'))

        symbol = QgsLineSymbol.createSimple({'line_style': 'dash', 'color': QColor('red'), 'width': '0.75'})

        vl.renderer().setSymbol(symbol)
        vl.triggerRepaint()

        for feature in path_layer.getFeatures():
            path_layer.deleteFeature(feature.id())

        features = []

        for points in path:
            features.append(Utils.create_polyline(points))

        pr.addFeatures(features)
        vl.commitChanges()

        d = QgsDistanceArea()
        d.setEllipsoid('WGS84')

        print(f'RoutePlanner::update_layer() - Track length {sum([d.measureLength(feature.geometry()) for feature in features]) / 1000:.2f} km')

    def subscribe_to_layers(self):
        print(f'RoutePlanner::subscribe_to_layers()')

        routes = Utils.get_or_create_tracks_directory()

        if not routes:
            return

        """
        for child in routes.children():
            for c in child.children():
                if c.name() == 'Points': # TODO: Refactor.
                    c.layer().editingStopped.connect(self.route_refresh)
                    # c.layer().geometryChanged.connect(self.route_refresh)
                    # c.layer().featureAdded.connect(self.route_refresh)
        """

    def remove_non_point_geometries(self, layer: QgsVectorLayer):
        print(f'RoutePlanner::remove_non_point_geometries() - From layer {Utils.get_parent_name(layer)}')

        layer.startEditing()

        for feature in layer.getFeatures():
            if feature.geometry().type() != QgsWkbTypes.PointGeometry:
                layer.deleteFeature(feature.id())

        layer.commitChanges()

    def get_active_track(self) -> QgsLayerTreeGroup|None:
        nodes = self.iface.layerTreeView().selectedNodes()

        print(nodes)

        if len(nodes) != 1:
            return None

        node = nodes[0]

        if node.parent() and node.parent().name() == 'Tracks':
            return node

        if node.name() in [Utils.LAYER_NAME_PATH, Utils.LAYER_NAME_POINT]:
            return node.parent()

        return None
