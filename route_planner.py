import html
import urllib.parse

from qgis.core import QgsProject, QgsRasterLayer
from qgis.gui import QgsMapToolPan
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .config import Config
from .file import File
from .iface import Iface
from .map_tools import Edit, PointCreateEnd, PointCreateMiddle, PointCreateStart, PointDelete, PointMove, StreetView, WaypointCreate, WaypointDelete, WaypointMove
from .options import Options
from .route_planner_dockwidget import RoutePlannerDockWidget
from .segment import Segment
from .track import Track
from .tree import Tree

from .resources import *


class RoutePlanner:
    def __init__(self, iface):
        print('RoutePlanner.__init__()')

        Iface.set(iface)

        self.iface = iface
        self.actions = []
        self.menu = '&RoutePlanner'
        self.toolbar = self.iface.addToolBar('RoutePlanner')
        self.toolbar.setObjectName('RoutePlanner')
        self.dockwidget = None

        # create tools
        self.mapToolPan = QgsMapToolPan(self.iface.mapCanvas())
        self.mapToolStreetView = StreetView(self.iface, self.iface.mapCanvas(), self.show_street_view)
        self.mapToolEdit = Edit(self.iface, self.iface.mapCanvas())

        self.mapToolWaypointCreate = WaypointCreate(self.iface, self.iface.mapCanvas())
        self.mapToolWaypointMove = WaypointMove(self.iface, self.iface.mapCanvas())
        self.mapToolWaypointDelete = WaypointDelete(self.iface, self.iface.mapCanvas())

        self.mapToolPointCreateStart = PointCreateStart(self.iface, self.iface.mapCanvas())
        self.mapToolPointCreateMiddle = PointCreateMiddle(self.iface, self.iface.mapCanvas())
        self.mapToolPointCreateEnd = PointCreateEnd(self.iface, self.iface.mapCanvas())
        self.mapToolPointMove = PointMove(self.iface, self.iface.mapCanvas())
        self.mapToolPointDelete = PointDelete(self.iface, self.iface.mapCanvas())

    def add_action(self, icon_path: str, text: str, callback, parent = None):
        print('RoutePlanner.add_action()')

        action = QAction(QIcon(icon_path), text, parent)
        action.triggered.connect(callback)
        action.setEnabled(True)

        self.toolbar.addAction(action)
        self.iface.addPluginToMenu(self.menu, action)

        return action

    def initGui(self):
        print('RoutePlanner.initGui()')

        action = self.add_action(':/plugins/route_planner/icon.png', text='Show', callback=self.run, parent=self.iface.mainWindow())

        if action is not None:
            self.actions.append(action)

    def onClosePlugin(self):
        print('RoutePlanner.onClosePlugin()')

        return
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.dockwidget = None

    def unload(self):
        print('RoutePlanner.unload()')

        for action in self.actions:
            self.iface.removePluginMenu('&RoutePlanner', action)
            self.iface.removeToolBarIcon(action)

        if self.dockwidget is not None:
            self.iface.removeDockWidget(self.dockwidget)
            self.dockwidget.deleteLater()

    def run(self):
        print('RoutePlanner.run()')

        if self.dockwidget is None:
            # create widget
            self.dockwidget = RoutePlannerDockWidget()
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # main modes
            self.dockwidget.buttonLoad.clicked.connect(lambda: Tree.create_tree_structure())
            self.dockwidget.buttonSelect.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolStreetView))
            self.dockwidget.buttonEdit.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolEdit))

            # setup file buttons
            self.dockwidget.buttonFileNew.clicked.connect(lambda: Segment.create(Track.create(File.new())))
            self.dockwidget.buttonFileOpen.clicked.connect(lambda: File.open())
            self.dockwidget.buttonFileReload.clicked.connect(lambda: File.reload(File.get_active(self.iface)))
            self.dockwidget.buttonFileSave.clicked.connect(lambda: File.save(File.get_active(self.iface)))
            self.dockwidget.buttonFileClose.clicked.connect(lambda: File.close(File.get_active(self.iface)))

            # setup waypoint buttons
            self.dockwidget.buttonWaypointCreate.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolWaypointCreate))
            self.dockwidget.buttonWaypointMove.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolWaypointMove))
            self.dockwidget.buttonWaypointDelete.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolWaypointDelete))

            # setup track buttons
            self.dockwidget.buttonTrackCreate.clicked.connect(lambda: Segment.create(Track.create(File.get_active(self.iface))))
            self.dockwidget.buttonTrackRefresh.clicked.connect(lambda: Track.refresh(Track.get_active(self.iface)))
            self.dockwidget.buttonTrackReverse.clicked.connect(lambda: Track.reverse(Track.get_active(self.iface)))
            self.dockwidget.buttonTrackOptimize.clicked.connect(lambda: Track.optimize(Track.get_active(self.iface)))
            self.dockwidget.buttonTrackDelete.clicked.connect(lambda: Track.delete(Track.get_active(self.iface)))

            # setup segment buttons
            self.dockwidget.buttonSegmentCreate.clicked.connect(lambda: Segment.create(Track.get_active(self.iface)))
            self.dockwidget.buttonSegmentRefresh.clicked.connect(lambda: Segment.refresh(Segment.get_active(self.iface)))
            self.dockwidget.buttonSegmentReverse.clicked.connect(lambda: Segment.reverse(Segment.get_active(self.iface)))
            self.dockwidget.buttonSegmentDelete.clicked.connect(lambda: Segment.delete(Segment.get_active(self.iface)))

            # setup point buttons
            self.dockwidget.buttonPointCreateStart.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolPointCreateStart))
            self.dockwidget.buttonPointCreateMiddle.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolPointCreateMiddle))
            self.dockwidget.buttonPointCreateEnd.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolPointCreateEnd))
            self.dockwidget.buttonPointMove.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolPointMove))
            self.dockwidget.buttonPointDelete.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolPointDelete))

            # setup routing options
            self.dockwidget.optionRouting.stateChanged.connect(lambda: Options.set_routing(self.dockwidget.optionRouting.isChecked()))
            self.dockwidget.optionRoutingProvider.currentTextChanged.connect(lambda: Options.set_routing_provider(self.dockwidget.optionRoutingProvider.currentText()))
            self.dockwidget.optionRoutingMode.currentTextChanged.connect(lambda: Options.set_routing_mode(self.dockwidget.optionRoutingMode.currentText()))
            self.dockwidget.optionAvoidHighways.setChecked(Options.avoid_highways)
            self.dockwidget.optionAvoidHighways.stateChanged.connect(lambda: Options.set_avoid_highways(self.dockwidget.optionAvoidHighways.isChecked()))
            self.dockwidget.optionAvoidTolls.setChecked(Options.avoid_tolls)
            self.dockwidget.optionAvoidTolls.stateChanged.connect(lambda: Options.set_avoid_tolls(self.dockwidget.optionAvoidTolls.isChecked()))

            # setup control point options
            self.dockwidget.spinBoxPointsPerSegment.setValue(Options.control_point_per_segment)
            self.dockwidget.spinBoxPointsPerSegment.valueChanged.connect(lambda: Options.set_control_point_per_segment(self.dockwidget.spinBoxPointsPerSegment.value()))
            self.dockwidget.spinBoxMinPointDistance.setValue(Options.control_point_min_distance)
            self.dockwidget.spinBoxMinPointDistance.valueChanged.connect(lambda: Options.set_control_point_min_distance(self.dockwidget.spinBoxMinPointDistance.value()))
            self.dockwidget.spinBoxMinAngle.setValue(Options.control_point_min_angle)
            self.dockwidget.spinBoxMinAngle.valueChanged.connect(lambda: Options.set_control_point_min_angle(self.dockwidget.spinBoxMinAngle.value()))

        # show widget
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
        self.dockwidget.show()

    def show_street_view(self, point):
        if self.dockwidget is None:
            return

        if self.dockwidget.streetViewBrowser is None:
            self.dockwidget.labelStreetView.setText('QtWebEngine is not available')
            return

        params = urllib.parse.urlencode({
            'key': Config.Google.Key,
            'location': f'{point.y()},{point.x()}',
        })
        url = f'https://www.google.com/maps/embed/v1/streetview?{params}'
        page = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    html, body, iframe {{
      width: 100%;
      height: 100%;
      margin: 0;
      border: 0;
      overflow: hidden;
    }}
  </style>
</head>
<body>
  <iframe src="{html.escape(url, quote=True)}" allowfullscreen></iframe>
</body>
</html>
"""

        self.dockwidget.streetViewBrowser.setHtml(page)
