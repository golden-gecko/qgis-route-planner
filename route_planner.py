import os.path

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .context_menu import ContextMenu
from .file import File
from .iface import Iface
from .map_tools import PointCreateEnd, PointCreateMiddle, PointCreateStart, PointDelete, PointMove
from .options import Options
from .route_planner_dockwidget import RoutePlannerDockWidget
from .segment import Segment
from .track import Track

from .resources import *


class RoutePlanner:
    def __init__(self, iface):
        Iface.set(iface)

        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        self.actions = []
        self.menu = '&RoutePlanner'
        self.toolbar = self.iface.addToolBar('RoutePlanner')
        self.toolbar.setObjectName('RoutePlanner')

        self.pluginIsActive = False
        self.dockwidget = None

    def add_action(self, icon_path, text, callback, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        action = QAction(QIcon(icon_path), text, parent)
        action.triggered.connect(callback)
        action.setEnabled(True)

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
        self.add_action(':/plugins/route_planner/icon.png', text='Show', callback=self.run, parent=self.iface.mainWindow())

    def onClosePlugin(self):
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.pluginIsActive = False

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu('&RoutePlanner', action)
            self.iface.removeToolBarIcon(action)

        del self.toolbar

    def run(self):
        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.dockwidget is None:
                self.dockwidget = RoutePlannerDockWidget()

            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # setup file buttons
            self.dockwidget.buttonFileNew.clicked.connect(lambda: Segment.create(Track.create(File.new())))
            self.dockwidget.buttonFileOpen.clicked.connect(lambda: File.open())
            self.dockwidget.buttonFileSave.clicked.connect(lambda: File.save(File.get_active(self.iface)))
            self.dockwidget.buttonFileClose.clicked.connect(lambda: File.close(File.get_active(self.iface)))

            # setup track buttons
            self.dockwidget.buttonTrackCreate.clicked.connect(lambda : Track.create(File.get_active(self.iface)))
            self.dockwidget.buttonTrackRefresh.clicked.connect(lambda: Track.refresh(Track.get_active(self.iface)))
            self.dockwidget.buttonTrackDelete.clicked.connect(lambda: Track.delete(Track.get_active(self.iface)))

            # setup segment buttons
            self.dockwidget.buttonSegmentCreate.clicked.connect(lambda : Segment.create(Track.get_active(self.iface)))
            self.dockwidget.buttonSegmentRefresh.clicked.connect(lambda: Segment.refresh(Segment.get_active(self.iface)))
            self.dockwidget.buttonSegmentDelete.clicked.connect(lambda: Segment.delete(Segment.get_active(self.iface)))

            # setup point buttons
            self.dockwidget.buttonPointCreateStart.clicked.connect(lambda: RoutePlanner.set_point_start_tool(self.iface))
            self.dockwidget.buttonPointCreateMiddle.clicked.connect(lambda: RoutePlanner.set_point_middle_tool(self.iface))
            self.dockwidget.buttonPointCreateEnd.clicked.connect(lambda: RoutePlanner.set_point_end_tool(self.iface))
            self.dockwidget.buttonPointMove.clicked.connect(lambda: RoutePlanner.set_point_move_tool(self.iface))
            self.dockwidget.buttonPointDelete.clicked.connect(lambda: RoutePlanner.set_point_delete_tool(self.iface))

            # setup options
            self.dockwidget.optionRouting.stateChanged.connect(lambda: Options.set_routing(self.dockwidget.optionRouting.isChecked()))
            self.dockwidget.optionRoutingProvider.addItems(['Google', 'MapQuest'])
            self.dockwidget.optionRoutingProvider.currentTextChanged.connect(lambda: Options.set_routing_provider(self.dockwidget.optionRoutingProvider.currentText()))

            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

            ContextMenu.create(self.iface.mapCanvas())

    @staticmethod
    def set_point_start_tool(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointCreateStart(iface, canvas))

    @staticmethod
    def set_point_middle_tool(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointCreateMiddle(iface, canvas))

    @staticmethod
    def set_point_end_tool(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointCreateEnd(iface, canvas))

    @staticmethod
    def set_point_move_tool(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointMove(iface, canvas))

    @staticmethod
    def set_point_delete_tool(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointDelete(iface, canvas))
