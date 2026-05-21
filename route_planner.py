from qgis.gui import QgsMapToolPan
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .file import File
from .iface import Iface
from .map_tools import Edit, PointCreateEnd, PointCreateMiddle, PointCreateStart, PointDelete, PointMove, WaypointCreate, WaypointDelete, WaypointMove
from .options import Options
from .route_planner_dockwidget import RoutePlannerDockWidget
from .segment import Segment
from .track import Track

from .resources import *


class RoutePlanner:
    def __init__(self, iface):
        Iface.set(iface)

        self.iface = iface
        self.actions = []
        self.menu = '&RoutePlanner'
        self.toolbar = self.iface.addToolBar('RoutePlanner')
        self.toolbar.setObjectName('RoutePlanner')
        self.dockwidget = None

        # create tools
        self.mapToolPan = QgsMapToolPan(self.iface.mapCanvas())
        self.mapToolEdit = Edit(self.iface, self.iface.mapCanvas())

        self.mapToolWaypointCreate = WaypointCreate(self.iface, self.iface.mapCanvas())
        self.mapToolWaypointMove = WaypointMove(self.iface, self.iface.mapCanvas())
        self.mapToolWaypointDelete = WaypointDelete(self.iface, self.iface.mapCanvas())

        self.mapToolPointCreateStart = PointCreateStart(self.iface, self.iface.mapCanvas())
        self.mapToolPointCreateMiddle = PointCreateMiddle(self.iface, self.iface.mapCanvas())
        self.mapToolPointCreateEnd = PointCreateEnd(self.iface, self.iface.mapCanvas())
        self.mapToolPointMove = PointMove(self.iface, self.iface.mapCanvas())
        self.mapToolPointDelete = PointDelete(self.iface, self.iface.mapCanvas())

    def add_action(self, icon_path, text, callback, parent = None):
        action = QAction(QIcon(icon_path), text, parent)
        action.triggered.connect(callback)
        action.setEnabled(True)

        self.toolbar.addAction(action)
        self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)

    def initGui(self):
        self.add_action(':/plugins/route_planner/icon.png', text='Show', callback=self.run, parent=self.iface.mainWindow())

    def onClosePlugin(self):
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.dockwidget = None

    def unload(self):
        self.iface.removeDockWidget(self.dockwidget)
        self.dockwidget.deleteLater()

        for action in self.actions:
            self.iface.removePluginMenu('&RoutePlanner', action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        self.dockwidget = RoutePlannerDockWidget()
        self.dockwidget.closingPlugin.connect(self.onClosePlugin)

        # main modes
        self.dockwidget.buttonSelect.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolPan))
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

        # setup options
        self.dockwidget.optionRouting.stateChanged.connect(lambda: Options.set_routing(self.dockwidget.optionRouting.isChecked()))
        self.dockwidget.optionRoutingProvider.currentTextChanged.connect(lambda: Options.set_routing_provider(self.dockwidget.optionRoutingProvider.currentText()))
        self.dockwidget.optionRoutingMode.currentTextChanged.connect(lambda: Options.set_routing_mode(self.dockwidget.optionRoutingMode.currentText()))
        self.dockwidget.spinBoxPointsPerSegment.setValue(Options.points_per_segment)
        self.dockwidget.spinBoxPointsPerSegment.valueChanged.connect(lambda: Options.set_points_per_segment(self.dockwidget.spinBoxPointsPerSegment.value()))
        self.dockwidget.spinBoxMinPointDistance.setValue(Options.min_point_distance)
        self.dockwidget.spinBoxMinPointDistance.valueChanged.connect(lambda: Options.set_min_point_distance(self.dockwidget.spinBoxMinPointDistance.value()))

        # show widget
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
        self.dockwidget.show()
