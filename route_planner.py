import math
import os
import requests

from qgis.PyQt.QtWebChannel import QWebChannel

from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry, QgsProject, QgsPointXY, QgsRasterLayer, QgsVectorFileWriter, QgsVectorLayer, QgsWkbTypes, QgsField, QgsFeature
from qgis.gui import QgsMapToolPan, QgsRubberBand, QgsVertexMarker
from qgis.PyQt.QtCore import Qt, QObject, pyqtSlot, pyqtSignal, QVariant
from qgis.PyQt.QtGui import QIcon, QPixmap, QColor
from qgis.PyQt.QtWidgets import QAction, QPushButton

from .config import Config
from .file import File
from .google import Google
from .iface import Iface
from .map_tools import Edit, PointCreateEnd, PointCreateMiddle, PointCreateStart, PointDelete, PointMove, StreetView, WaypointCreate, WaypointDelete, WaypointMove
from .options import Options
from .route_planner_dockwidget import RoutePlannerDockWidget
from .segment import Segment
from .track import Track
from .tree import Tree
from .utils import Utils

from . import resources_rc


class Bridge(QObject):
    posChanged = pyqtSignal(float, float, float, float)

    @pyqtSlot(float, float, float, float)
    def onPos(self, lat, lng, heading, pitch):
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
        self.bridge = Bridge()
        self.bridge.posChanged.connect(self._on_streetview_pos)

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

        self.streetViewHeadingBand = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.GeometryType.LineGeometry)
        self.streetViewHeadingBand.setColor(QColor('red'))
        self.streetViewHeadingBand.setWidth(2)

        # connect to map canvas movement to get center coordinates (map moved)
        self.iface.mapCanvas().extentsChanged.connect(self._on_map_moved)

    def add_action(self, icon_path: str, text: str, callback, parent = None):
        print('RoutePlanner.add_action()')

        path = os.path.join(os.path.dirname(__file__), os.path.basename(icon_path))

        if os.path.exists(path):
            icon = QIcon(path)
        else:
            icon = QIcon()

        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(True)

        self.toolbar.addAction(action)
        self.iface.addPluginToMenu(self.menu, action)
        self.toolbar.repaint()

        return action

    def initGui(self):
        print('RoutePlanner.initGui()')

        action = self.add_action(':/plugins/route_planner/icon.png', text='Route Planner', callback=self.run, parent=self.iface.mainWindow())

        if self.toolbar is not None:
            self.toolbar.show()

        if action is not None:
            self.actions.append(action)

    def destroy_heading_band(self):
        print('RoutePlanner.destroy_heading_band()')

        if self.streetViewHeadingBand is not None:
            self.iface.mapCanvas().scene().removeItem(self.streetViewHeadingBand)
            self.streetViewHeadingBand = None

    def onClosePlugin(self):
        print('RoutePlanner.onClosePlugin()')

        try:
            self.iface.mapCanvas().extentsChanged.disconnect(self._on_map_moved)
            self.destroy_heading_band()
        except Exception as e:
            print(e)

    def unload(self):
        print('RoutePlanner.unload()')

        for action in self.actions:
            try:
                self.iface.removePluginMenu('&RoutePlanner', action)
                self.iface.removeToolBarIcon(action)
                action.deleteLater()
            except Exception as e:
                print(e)

        try:
            self.iface.mapCanvas().extentsChanged.disconnect(self._on_map_moved)
        except Exception as e:
            print(e)

        try:
            self.destroy_heading_band()
        except Exception as e:
            print(e)

        if self.dockwidget is not None:
            try:
                self.iface.removeDockWidget(self.dockwidget)
                self.dockwidget.deleteLater()
                self.dockwidget = None
            except Exception as e:
                print(e)

        if self.toolbar is not None:
            try:
                self.iface.mainWindow().removeToolBar(self.toolbar)
                self.toolbar.deleteLayer()
                self.toolbar = None
            except Exception as e:
                print(e)

    def load_panoramas(self):
        print('RoutePlanner.load_panoramas()')

        layer = Tree.find_layer_by_path(Config.Panoramas.Path)

        if layer is None:
            layer = QgsVectorLayer("Point?crs=EPSG:4326", "Panoramas", "memory")
            Utils.add_layer(Tree.get_root(), layer)

        pr = layer.dataProvider()

        # ensure fields 'pano_id' and 'date' exist
        added_fields = []
        if layer.fields().indexFromName('pano_id') == -1:
            added_fields.append(QgsField('pano_id', QVariant.String))
        if layer.fields().indexFromName('date') == -1:
            added_fields.append(QgsField('date', QVariant.String))
        if added_fields:
            pr.addAttributes(added_fields)
            layer.updateFields()

        # collect existing pano ids to avoid duplicates
        idx_pano = layer.fields().indexFromName('pano_id')
        existing_ids = set()
        if idx_pano != -1:
            for feat in layer.getFeatures():
                val = feat.attribute(idx_pano)
                if val is not None:
                    existing_ids.add(str(val))

        canvas = self.iface.mapCanvas()

        center = canvas.extent().center()

        # determine source CRS (canvas map CRS) and transform to WGS84 (EPSG:4326)
        src_crs = canvas.mapSettings().destinationCrs()

        dest_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        xform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
        lonlat = xform.transform(center)
        lon = lonlat.x()
        lat = lonlat.y()

        # fetch nearby panoramas via Google API
        panoramas = Google.get_nearby_panoramas(lat, lon, radius=200, max_results=10)
        print(f'Found {len(panoramas)} panoramas near center:')

        new_feats = []
        for p in panoramas:
            pano_id = p.get('pano_id') or f"{p.get('lat')}:{p.get('lng')}"
            if pano_id in existing_ids:
                print(f'  skipping existing pano {pano_id}')
                continue

            plat = p.get('lat')
            plng = p.get('lng')
            if plat is None or plng is None:
                continue

            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(plng, plat)))

            # build attributes matching layer fields
            attrs = [None] * layer.fields().count()
            idx_date = layer.fields().indexFromName('date')
            if idx_pano != -1:
                attrs[idx_pano] = str(pano_id)
            if idx_date != -1:
                attrs[idx_date] = str(p.get('date') or '')

            f.setAttributes(attrs)
            new_feats.append(f)
            print(f"  added pano {pano_id} at {plat},{plng}")

        if new_feats:
            pr.addFeatures(new_feats)

            layer.commitChanges()
            layer.updateExtents()
            layer.triggerRepaint()

        self.iface.mapCanvas().refresh()

    def run(self):
        print('RoutePlanner.run()')

        if self.dockwidget is None:
            # create widget
            self.dockwidget = RoutePlannerDockWidget()
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # main modes
            self.dockwidget.buttonTree.clicked.connect(lambda: Tree.create_tree_structure())
            self.dockwidget.buttonStreetView.clicked.connect(lambda: self.iface.mapCanvas().setMapTool(self.mapToolStreetView))
            self.dockwidget.buttonPanoramas.clicked.connect(lambda: self.load_panoramas())
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
        self.iface.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockwidget)
        self.dockwidget.show()

    def show_street_view(self, point):
        if self.dockwidget is None:
            return

        if self.dockwidget.streetViewBrowser is None:
            return

        page = f"""
            <!doctype html>
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
                        const pos = {{
                            lat: {point.y()},
                            lng: {point.x()}
                        }};
    
                        panorama = new google.maps.StreetViewPanorama(
                            document.getElementById('pano'), {{
                                position: pos,
                                pov: {{
                                    heading:0,
                                    pitch:0
                                }},
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

        ch = QWebChannel(self.dockwidget.streetViewBrowser.page())
        ch.registerObject('bridge', self.bridge)

        self.dockwidget.streetViewBrowser.page().setWebChannel(ch)

    def _on_streetview_pos(self, lat, lng, heading, pitch):
        pt_wgs84 = QgsPointXY(lng, lat)

        r = 6378137.0 # earth radius in meters
        d = 100.0     # arrow length in meters

        brng = math.radians(heading)
        lat1 = math.radians(lat)
        lon1 = math.radians(lng)
        lat2 = math.asin(math.sin(lat1) * math.cos(d / r) + math.cos(lat1) * math.sin(d / r) * math.cos(brng))
        lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(d / r) * math.cos(lat1), math.cos(d / r) - math.sin(lat1) * math.sin(lat2))
        dest_wgs84 = QgsPointXY(math.degrees(lon2), math.degrees(lat2))

        src_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        dest_crs = QgsProject.instance().crs()
        xform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
        pt = xform.transform(pt_wgs84)
        dest_pt = xform.transform(dest_wgs84)

        self.streetViewHeadingBand.setToGeometry(QgsGeometry.fromPolylineXY([pt, dest_pt]), None)

    def _on_map_moved(self):
        canvas = self.iface.mapCanvas()
        center = canvas.extent().center()

        # determine source CRS (canvas map CRS) and transform to WGS84 (EPSG:4326)
        src_crs = canvas.mapSettings().destinationCrs()

        dest_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        xform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
        lonlat = xform.transform(center)
        lon = lonlat.x()
        lat = lonlat.y()

        # execute desired code here — example: print center coordinates
        print(f'Map moved. Center (lat, lon): {lat}, {lon}')

