from qgis.core import QgsProject, QgsRasterLayer, QgsPointXY
from qgis.gui import QgsMapToolPan, QgsVertexMarker
from qgis.PyQt.QtCore import Qt, QObject, pyqtSlot, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

try:
    from qgis.PyQt.QtWebChannel import QWebChannel
except Exception:
    try:
        from PyQt5.QtWebChannel import QWebChannel
    except Exception:
        try:
            from PyQt6.QtWebChannel import QWebChannel
        except Exception:
            try:
                from PySide2.QtWebChannel import QWebChannel
            except Exception:
                QWebChannel = None

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

class Bridge(QObject):
    posChanged = pyqtSignal(float, float, float, float)

    @pyqtSlot(float, float, float, float)
    def onPos(self, lat, lng, heading, pitch):
        # Called from JS via QWebChannel
        self.posChanged.emit(lat, lng, heading, pitch)


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
        self.streetViewMarker = None

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

        lat = point.y()
        lng = point.x()
        page = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>html,body,#pano{{width:100%;height:100%;margin:0}}</style>
</head>
<body>
  <div id="pano"></div>
  <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
  <script>
    let panorama;
    function initialize() {{
      const pos = {{lat: {lat}, lng: {lng}}};
      panorama = new google.maps.StreetViewPanorama(
        document.getElementById('pano'),
        {{
          position: pos,
          pov: {{heading:0, pitch:0}},
          addressControl: false,
          linksControl: false
        }}
      );

      new QWebChannel(qt.webChannelTransport, function(channel) {{
        window.bridge = channel.objects.bridge;
        function send() {{
          const p = panorama.getPosition();
          const pov = panorama.getPov();
          bridge.onPos(p.lat(), p.lng(), pov.heading || 0, pov.pitch || 0);
        }}
        panorama.addListener('position_changed', send);
        panorama.addListener('pov_changed', send);
        send();
      }});
    }}
  </script>
  <script src="https://maps.googleapis.com/maps/api/js?key={Config.Google.Key}&callback=initialize&v=weekly" defer></script>
</body>
</html>
"""

        self.dockwidget.streetViewBrowser.setHtml(page)

        # setup QWebChannel bridge so JS can notify Python about position/pov changes
        if getattr(self, 'bridge', None) is None:
            self.bridge = Bridge()
            self.bridge.posChanged.connect(self._on_streetview_pos)
        if QWebChannel is not None:
            ch = QWebChannel(self.dockwidget.streetViewBrowser.page())
            ch.registerObject('bridge', self.bridge)
            self.dockwidget.streetViewBrowser.page().setWebChannel(ch)
        else:
            # Qt WebChannel not available; cannot receive JS updates
            pass

    def _on_streetview_pos(self, lat, lng, heading, pitch):
        # lat, lng: floats in degrees
        # create marker if needed
        if self.streetViewMarker is None:
            self.streetViewMarker = QgsVertexMarker(self.iface.mapCanvas())
            self.streetViewMarker.setColor(Qt.red)
            try:
                self.streetViewMarker.setIconSize(12)
                self.streetViewMarker.setIconType(QgsVertexMarker.ICON_CROSS)
            except Exception:
                pass
            self.streetViewMarker.setPenWidth(3)
        pt_wgs84 = QgsPointXY(lng, lat)
        # transform to project CRS
        try:
            from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
            src_crs = QgsCoordinateReferenceSystem('EPSG:4326')
            dest_crs = QgsProject.instance().crs()
            xform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
            pt = xform.transform(pt_wgs84)
        except Exception:
            # fallback to using WGS84 coords if transform unavailable
            pt = pt_wgs84

        self.streetViewMarker.setCenter(pt)
        # center map on the panorama position
        try:
            self.iface.mapCanvas().setCenter(pt)
            self.iface.mapCanvas().refresh()
        except Exception:
            pass
