# QGIS Route Planner

A lightweight QGIS plugin for planning and managing routes inside QGIS.

## Supported path-finding APIs

- Google Directions API — Commercial routing service (API key required).
- GraphHopper — Routing and optimization via HTTP API.
- Mapbox Directions API — Commercial directions API (requires access token).

## Supported tile providers

- Bing
- Google Maps
- Mapbox
- OpenStreetMap

## Installation

- Unpack into your QGIS plugins directory.
   - on Linux `~/.local/share/QGIS/QGIS4/profiles/default/python/plugins/`
   - on Windows `%APPDATA%\QGIS\QGIS$\profiles\default\python\plugins\`
- Copy `config.py.example` into `config.py` and edit it to add your API keys.
- Then, enable the plugin in QGIS via `Plugins > Manage and Install Plugins...`.
- Click on the `Route Planner` icon in the toolbar to open the plugin.
- Click on `Tree` button to load configuration. The plugin will create `RoutePlanner` folder in layer tree.
