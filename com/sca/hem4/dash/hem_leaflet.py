# -*- coding: utf-8 -*-
"""
Created on Mon May 23 09:08:26 2022

@author: mmorr
"""

# import pandas as pd
# import polars as pl
# import geopandas as gp
# import numpy as np
import dash_leaflet as dl
# import dash_leaflet.express as dlx
# from dash_extensions.javascript import assign, arrow_function
# import json


def get_basemaps():
    aerial = dl.BaseLayer(dl.TileLayer(url='https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}',
                               attribution = 'Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>'),
                  name = 'satellite1')
    esri = dl.BaseLayer(dl.TileLayer(url = 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                                      attribution = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'),
                        name = 'Satellite', checked = False)
    # dark = dl.BaseLayer(dl.TileLayer(url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
    #                                  attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'),
    #                            name = 'Dark', checked = True)
    dark = dl.BaseLayer(dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                                     attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
                                     name = 'Dark', checked = True)
    # light = dl.BaseLayer(dl.TileLayer(url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png',
    #                      attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'),
    #                            name = 'Light', checked = False)
    light = dl.BaseLayer(dl.TileLayer(url = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                         attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
                               name = 'Light', checked = False)
    openstreet = dl.BaseLayer(dl.TileLayer(url='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                               attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'), name='OpenStreetMap')
    # roads =  dl.Overlay(dl.TileLayer(url = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer/tile/{z}/{y}/{x}',
    #                                  attribution = 'U.S. Census Bureau'),
    #               name = 'Roads')
    roads =  dl.Overlay(dl.TileLayer(url = 'https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png',
                                      attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
                  name = 'Roads/Places')
    # roads =  dl.Overlay(dl.TileLayer(url = 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain-labels/{z}/{x}/{y}{r}.{ext}',
    #                                  attribution = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'),
    #               name = 'Roads/Places')
    
    return esri, dark, light, openstreet, roads


    