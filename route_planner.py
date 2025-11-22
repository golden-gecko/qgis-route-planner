import os.path

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .context_menu import ContextMenu
from .iface import Iface
from .map_tools import PointCreateEnd, PointCreateMiddle, PointCreateStart, PointDelete, PointMove
from .options import Options
from .route_planner_dockwidget import RoutePlannerDockWidget
from .track import Track

from .resources import *


class RoutePlanner:
    def __init__(self, iface):
        print('RoutePlanner::__init__()')

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
        print('RoutePlanner::add_action()')

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
        print('RoutePlanner::initGui()')

        self.add_action(':/plugins/route_planner/icon.png', text='Show', callback=self.run, parent=self.iface.mainWindow())

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

            self.dockwidget.buttonTrackCreate.clicked.connect(lambda : Track.create())
            self.dockwidget.buttonTrackDelete.clicked.connect(lambda: Track.delete(self.iface))
            self.dockwidget.buttonTrackEdit.clicked.connect(lambda: Track.edit(self.iface))
            self.dockwidget.buttonTrackRefresh.clicked.connect(lambda: Track.refresh_active(self.iface))

            self.dockwidget.buttonTrackOpen.clicked.connect(lambda: Track.open(self.iface))
            self.dockwidget.buttonTrackSave.clicked.connect(lambda: Track.save(self.iface))

            self.dockwidget.buttonPointCreateStart.clicked.connect(lambda: RoutePlanner.create_start_tool(self.iface))
            self.dockwidget.buttonPointCreateMiddle.clicked.connect(lambda: RoutePlanner.create_middle_tool(self.iface))
            self.dockwidget.buttonPointCreateEnd.clicked.connect(lambda: RoutePlanner.create_end_tool(self.iface))
            self.dockwidget.buttonPointDelete.clicked.connect(lambda: RoutePlanner.delete_tool(self.iface))
            self.dockwidget.buttonPointMove.clicked.connect(lambda: RoutePlanner.move_tool(self.iface))

            self.dockwidget.optionRouting.stateChanged.connect(lambda: Options.set_routing(self.dockwidget.optionRouting.isChecked()))
            self.dockwidget.optionRoutingProvider.addItems(['Google', 'MapQuest'])
            self.dockwidget.optionRoutingProvider.currentTextChanged.connect(lambda: Options.set_routing_provider(self.dockwidget.optionRoutingProvider.currentText()))

            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

            ContextMenu.create(self.iface.mapCanvas())

    @staticmethod
    def create_start_tool(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointCreateStart(iface, canvas))

    @staticmethod
    def create_middle_tool(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointCreateMiddle(iface, canvas))

    @staticmethod
    def create_end_tool(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointCreateEnd(iface, canvas))

    @staticmethod
    def delete_tool(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointDelete(iface, canvas))

    @staticmethod
    def move_tool(iface):
        canvas = iface.mapCanvas()
        canvas.setMapTool(PointMove(iface, canvas))
