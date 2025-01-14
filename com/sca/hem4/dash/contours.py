# -*- coding: utf-8 -*-
"""
Created on Wed May  3 15:14:22 2023

@author: SteveFudge
"""

import dash
from dash import dash_table
from dash import Dash, html, Input, Output, State, no_update, dcc
from dash_extensions.javascript import assign, arrow_function, Namespace
from dash_extensions.enrich import callback_context
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx

import plotly.graph_objects as go 
import subprocess, webbrowser
from threading import Timer
import pandas as pd
import numpy as np
from numpy import sin, cos, arcsin, pi, sqrt
import plotly.express as px
import plotly
import os
from tkinter import messagebox

from flask import request
import time

# Imports needed specifically for making contour maps
from com.sca.hem4.dash.hem_leaflet import get_basemaps
import matplotlib.pyplot as plt
import geojsoncontour
import json
import geopandas as gp
from scipy.interpolate import griddata
from sigfig import round as roundsf
import io
import base64
import sys


class contours():
    
    def __init__(self):
        pass
    
    def resource_path(self, relative_path):
        # get absolute path to resource
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            cd = os.path.abspath(".")
            base_path = os.path.join(cd, 'com\\sca\\hem4\\dash')
                
        return os.path.join(base_path, relative_path)

    def make_alert(self, string):
        if string is None:
            return no_update
        else:        
            alert = dbc.Alert(                
                string,
                color = 'danger',
                dismissable=True,
                is_open=True,
                duration=5000
            )
            
            return alert
        
    def riskfig(self, numb, digz):
        numtype = float if numb < 1 else int
        return roundsf(numb,sigfigs = digz, output_type = numtype)


    def buildApp(self):
                 
        ## Rather than using the external css, could use local "assets" dir that has the css file
        # external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        dbc_stylesheets = [dbc.themes.MORPH]
        
        # External scripts
        chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js"  # js lib used for colors
                
        ct_esri, ct_dark, ct_light, ct_openstreet, ct_places, ct_roads = get_basemaps() # get basemaps and other layers                

        # These are for the contour map tab
        metrics = {'Cancer Risk (in a million)':'MIR', 'Respiratory HI':'Respiratory HI', 'Liver HI':'Liver HI',
                   'Neurological HI':'Neurological HI', 'Developmental HI':'Developmental HI',
                   'Reproductive HI':'Reproductive HI', 'Kidney HI':'Kidney HI', 'Ocular HI':'Ocular HI',
                    'Endocrine HI':'Endocrine HI', 'Hematological HI':'Hematological HI', 'Immunological HI':'Immunological HI',
                    'Skeletal HI':'Skeletal HI', 'Spleen HI':'Spleen HI', 'Thyroid HI':'Thyroid HI', 'Whole body HI':'Whole body HI'}
        metrics_reversed = {value: key for key, value in metrics.items()}

        coloramps = ['viridis', 'magma', 'cividis', 'rainbow', 'gist_earth','terrain','jet', 'turbo',
                      'ocean', 'tab10',
                      'Blues', 'Greens', 'Oranges', 'Reds',
                      'viridis_r', 'magma_r', 'cividis_r', 'rainbow_r', 'gist_earth_r','terrain_r','jet_r', 'turbo_r',
                      'ocean_r', 'tab10_r',
                      'Blues_r', 'Greens_r', 'Oranges_r', 'Reds_r']
                
        app = dash.Dash(__name__, external_stylesheets=dbc_stylesheets, 
                        external_scripts=[chroma], assets_folder=self.resource_path('assets'))
        app.title = 'HEM Contour Maps'
        
        modal = html.Div(
            [
                dbc.Button("About the Contours", id="modalbutton", n_clicks=0),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("About the Contours")),
                        dbc.ModalBody(
                            dcc.Markdown('''
                                           
> The contours are generated using the griddata (linear) interpolation method of the [SciPy](https://scipy.org/) Python library.\
    There is inherent uncertainty involved in any interpolation. The contour interpolation is more accurate \
        when more input data are used, so it is recommended that your polar receptor network have at least the \
            default number of rings (13) and radials (16). Including the census block receptors may increase \
                resolution near the facility, although too many receptors can cause undesired irregular contour edges. \
                    Experiment using ring summary with and without block summary data, to balance contour \
                        smoothness with resolution around the modeled facility.
        
> To expedite loading, the contoured area is limited to no more than 20km from the location of maximum impact, where the risks are the highest.\
    The boundary of the contoured area could be rectangular, circular, or irregular depending on the size of your modeling domain \
        and whether your contours are based on ring summary with or without block summary data.

> If your contours are based on both unpopulated receptors (e.g., polar rings) and populated receptors (e.g., census blocks),\
    and you are using the automatically generated class breaks, unpopulated areas of higher impact (than predicted for populated receptors)\
        may appear close to the facility as areas outside the color-coded contours. Note: To include unpopulated areas of higher impact\
            in the maximum contour, you can use the  “Input list of class breaks” option to enter a class break higher than the populated max impact (but ≤ the unpopulated max impact).                                        

> See the HEM User’s Guide for further discussion regarding the shape of the contours with respect to the modeled receptors and using the contours as part of QA review for your risk modeling.
                                            
                                        ''')
                                        ),                        
                    ],
                    id="modal",
                    is_open=False,
                ),
            ]
        )
                    
        app.layout = html.Div([
                                                               
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Row([
                                                      
                            dbc.Col(dbc.NavbarBrand("HEM Risk Contour Maps", className="ml-auto mr-auto",
                                                    style={"text-align": "center", 'font-weight': 'bold'})),
                            
                                ],
                            
                            align="center",
                            className="g-0",
                            ),                        
                        
                        modal,
                        
                    ]
                ),
                # color="primary",
                # dark=True,
            ),
            
                           
                html.Div([
                
                dbc.Container([
                    
                        dcc.Store(id='ctab-store-rawdata'),
                        dcc.Store(id='ctab-store-metricdata'),
                        dcc.Store(id='ctab-store-facid'),
                        dcc.Store(id='ctab-store-cont-json'),
                                
                        dbc.Row([
                            
                            dbc.Col([
                                dcc.Loading([
                                    
                                    html.H5('Select files to create contours', id='ctab-map-title')
                                    
                                    ], type = 'default')                                   
                                    
                                ], width={'size':8, 'offset':2})
                            
                            ]),
                
                        dbc.Row([
                            
                            dbc.Col([
                                
                                # html.Button('Upload File', id='upload-button'),
                                # dcc.Upload(id='ctab-upload-data', children=html.Div(['Drag and drop or click to select a file']))
                                
                                dcc.Upload(['Select Facility File(s)'],
                                    
                                            id='ctab-upload-data',
                                            multiple = True,
                                            accept = '.csv',
                                            style={
                                               
                                                'width': '100%',
                                                'height': '60px',
                                                'lineHeight': '60px',
                                                'backgroundColor': '#0275d8',
                                                'color': '#FFFFFF',
                                                'borderWidth': '2px',
                                                'borderStyle': 'solid',
                                                'borderRadius': '5px',
                                                'textAlign': 'center',
                                                'cursor': 'pointer'
                                            }),
                                                                
                                html.Div(id='ctab-upload-alert-div'),
                                                                       
                                dbc.Tooltip(                        
                                    [html.P('Select ring summary and/or block summary files'),
                                    html.P('Found in your HEM output dir\<your model run group>\<facility ID> folder')],
                                    target='ctab-upload-data',
                                    style={'backgroundColor': '#FFFFFF',
                                           'opacity': '1.0',
                                           'borderRadius': '4px'},
                                    class_name="fw-bold"
                                ),
                                
                                # html.Br(),
                                html.Label(["Risk metric"]),
                                dcc.Dropdown(id='ctab-metricdrop',
                                              options=[],
                                              multi=False,
                                              clearable=False,
                                              value=[],
                                              placeholder="Select a Metric",
                                              ),
                                dbc.Tooltip(                        
                                    [html.P('After you load data, only risk metrics with at least one\
                                            nonzero value will be included in this dropdown menu')],
                                    target='ctab-metricdrop',
                                    trigger = 'click hover focus legacy',
                                    style={'backgroundColor': '#FFFFFF',
                                           'opacity': '1.0',
                                           'borderRadius': '4px'},
                                    class_name="fw-bold"
                                ),
                                html.Div(id='ctab-metric-alert-div'),
                                                
                                html.Hr(),
                                html.Label(["Number of classes"]),
                                                    
                                dcc.Slider(2, 10, 1,
                                            value=5,
                                            id='ctab-classesdrop'
                                            ),
                                                    
                                dbc.Tooltip(                        
                                    [html.P('This will use the low and high values of your data, with this number of classes')],
                                    target='ctab-classesdrop',
                                    style={'backgroundColor': '#FFFFFF',
                                           'opacity': '1.0',
                                           'borderRadius': '4px'},
                                    class_name="fw-bold"
                                ),
                                
                                html.H6('OR', style={'textAlign': 'center', 'color': '#7FDBFF', 'font-weight' : 'bold'}),
                                html.Label(["Input list of class breaks"]),
                                html.Datalist(id="ctab-userlist", children=[
                                    html.Option(value= '100, 200, 300, 400, 500, 600, 700, 800, 900, 1000'),
                                    html.Option(value='10, 20, 40, 60, 80, 100'),
                                    html.Option(value='100, 200, 500, 1300, 3000'),
                                    html.Option(value='.1, .2, .5, 1, 2, 5, 10'),
                                    html.Option(value='.1, .3, 1, 3, 10'),
                                    ]),
                                dcc.Input(id='ctab-classinput', type = 'text', list = 'ctab-userlist', debounce = True),                    
                                dbc.Tooltip(                        
                                    [html.P('If you input your own class breaks (comma-separated list),\
                                            the number of classes above will be ignored'),
                                      html.P('Press enter after you input', style={'font-weight':'bold', 'font-style':'italic', 'color':'red'})],
                                    target='ctab-classinput',
                                    style={'backgroundColor': '#FFFFFF',
                                           'opacity': '1.0',
                                           'borderRadius': '4px'},
                                    class_name="fw-bold"
                                ),
                                
                                html.Hr(),
                                html.Label(["Color ramp"]),
                                dcc.Dropdown(id='ctab-rampdrop',
                                              options=[{"label": i, "value": i} for i in coloramps],
                                              multi=False,
                                              clearable=False,
                                              value = 'viridis',
                                              placeholder="Select Color Ramp",
                                              ),
                                                                                    
                                # html.Hr(),
                                html.Label(["Opacity"]),
                                dcc.Slider(.1, 1, .1,
                                            value=.8,
                                            marks=None,
                                            id='ctab-opacdrop'
                                            ),
                                
                                # html.Hr(),
                                html.Label(["Significant figures displayed"]),
                                dcc.RadioItems([1,2,3], 1, id='ctab-sigfigdrop', labelStyle={'display': 'inline-block', 'margin-right': '20px'}),
                                                    
                                                    
                                html.Hr(),
                                html.Div([
                                    
                                    dbc.Button("Download Data\n", id="ctab-open-offcanvas0",
                                                className="mx-auto", outline=True, color="primary", n_clicks=0)
                                    ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center'}),
                                
                                dbc.Offcanvas(
                                                    
                                                dbc.Row([
            
                                                        dbc.Col([
                                                                # dbc.Button("Download Contour as Shapefile", id="download-shapefile-button", n_clicks=0),
                                                                # dcc.Download(id="download-cont-shapefile"),
                                                                
                                                                dbc.Button("Download Contour as GeoJSON", id="download-json-button", n_clicks=0),
                                                                dcc.Download(id="download-cont-geojson")
                                                                
                                                                                                                                                            
                                                                ], width = 12, className="opacity-100"),
                                                        
                                                                
                                                ], className="opacity-100"),    
                                                
                                                id="ctab-offcanvas0",
                                                is_open=False,
                                            ),
                                                            
                                ], width = 2),
                
                            
                            dbc.Col([
                                                                                            
                                    dl.Map(id = 'ctab-themap', center = [39., -97.3], minZoom = 3, zoomSnap = .3,
                                            zoom=4, children=[
                                                dl.LayersControl([ct_esri, ct_dark, ct_light, ct_openstreet],)
                                                ],
                                            style={'width': '1200px', 'height': '600px'}),
                                    html.Div(style={
                                        'fontFamily': 'Arial, sans-serif',
                                        'fontSize': '12px',
                                        'fontWeight': 'bold',
                                        # 'color': 'black',
                                        'textAlign': 'left'
                                    },
                                        children=[
                                            html.P('* To expedite loading, the contoured area is limited to no more than 20km\
                                                   from the location of maximum impact.', style={'marginBottom': '1px'}),
                                            html.Div(id='block-footer')
                                        
                                        ]
                                    )
                                                                            
                                    ], width=10)
                                                     
                        ])
                        
                    ], fluid=True, style={"height": "90vh"})
                                            
                ], style={'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}),
                                            
                   
        ])
            



# Callbacks for the contours tab
        @app.callback(
                   Output('ctab-metric-alert-div', 'children'),
                   Output('ctab-themap', 'children'),
                   Output('ctab-map-title', 'children'),
                   Output('ctab-themap', 'zoom'),
                   Output('ctab-themap', 'center'),
                   Output('ctab-store-cont-json', 'data'),
              
                  Input('ctab-store-metricdata', 'data'),
                  Input('ctab-metricdrop','value'),
                  Input('ctab-classinput', 'value'),
                  Input('ctab-opacdrop', 'value'),
                  Input('ctab-classesdrop', 'value'),
                  Input('ctab-rampdrop', 'value'),
                  Input('ctab-sigfigdrop', 'value'),
                  Input('ctab-store-facid', 'data'),
                  Input('ctab-upload-data', 'filename'),
                  Input('ctab-store-rawdata', 'data')
                 
                  )
        
        def interp_contour(metdata, metric, usercls, opac, numclass, ramp, digz, facname, filelist, rawdata):
            
            if rawdata is None:
                maptitle = html.H4('Select files to create contours')
                return no_update, no_update, maptitle, no_update, no_update, no_update
            elif metric is None:
                maptitle = html.H4('Select a risk metric')
                return no_update, no_update, maptitle, no_update, no_update, no_update
                
            elif metdata is None:
                return no_update, no_update, no_update, no_update, no_update, no_update
            else:
                ctx = callback_context
                comp_id = ctx.triggered[0]['prop_id'].split('.')[0]
                dfpl = pd.DataFrame(metdata)
                block_max_val = None
                        
                if dfpl[metric].max() == 0:
                    alert = self.make_alert('There are no nonzero values for this metric')
                    return alert, no_update, no_update, no_update, no_update, no_update
                else:
                    gdf = gp.GeoDataFrame(
                        dfpl, geometry=gp.points_from_xy(dfpl.Longitude, dfpl.Latitude), crs="EPSG:4326")
                    
                    if metric == 'MIR':
                        if gdf['RecID'].str.contains('UCONC').any():
                            maptitle = html.H4('User-Supplied Concentrations - Lifetime Cancer Risk (in a million)')
                        else:
                            maptitle = html.H4(f'Facility {facname} - Lifetime Cancer Risk (in a million)')
                    else:
                        if gdf['RecID'].str.contains('UCONC').any():
                            maptitle = html.H4(f'User-Supplied Concentrations - {metric}')
                        else:
                            maptitle = html.H4(f'Facility {facname} - {metric}')
                                            
                    # Limit the size of the area to contour
                    span = abs(dfpl['Latitude'].max() - dfpl['Latitude'].min())*111133/1000
                    if gdf['RecID'].str.contains('ang|UCONC').any():
                        if span > 40:
                            cont_radius = 20
                        else:
                            cont_radius = round(span/2)
                            # cont_radius = round(span/sqrt(8))
                    else:
                        cont_radius = round(span/2)
                        
                    # Use the max receptor to center the map
                    max_x = dfpl.loc[dfpl[metric].idxmax()]
                    avglat = max_x['Latitude'] 
                    avglon = max_x['Longitude']
                    fac_center = [avglon, avglat]
                    
                    # Calculate the extents of the contour area
                    r_earth = 6371                    
                    lat2 = fac_center[1]  + (cont_radius / r_earth) * (180 / pi)
                    lon2 = fac_center[0] + (cont_radius / r_earth) * (180 / pi) / cos(np.deg2rad(fac_center[1]))
                    lat1 = fac_center[1]  - (cont_radius / r_earth) * (180 / pi)
                    lon1 = fac_center[0] - (cont_radius / r_earth) * (180 / pi) / cos(np.deg2rad(fac_center[1]))
                    
                    # Create separate layers for polar and block receptors
                    # The block layer does not include receptors from the user-supplied concentration option
                    polar_recpts = gdf.loc[gdf['RecID'].str.contains('ang')].copy()
                    block_recpts = gdf.loc[~gdf['RecID'].str.contains('ang|UCONC')].copy()
                                                               
                    if polar_recpts is not None and len(polar_recpts) != 0:
                        polar_recpts['Distance (m)'] = [x.split('ang')[0] for x in polar_recpts['RecID']]
                        polar_recpts['Angle (deg)'] = [x.split('ang')[1] for x in polar_recpts['RecID']]
                        if metric == 'MIR':
                            polar_recpts['tooltip'] = '<b>Polar Receptor</b>' +  '<br><b>Distance (m): </b>' + polar_recpts['Distance (m)'] \
                                + '<br><b>Angle (deg): </b>' + polar_recpts['Angle (deg)'] + '<br><b>Cancer Risk (in a million): </b>'\
                                + polar_recpts[metric].apply(lambda x: f'{self.riskfig(x, digz)}').astype(str)
                        else:
                            polar_recpts['tooltip'] = '<b>Polar Receptor</b>' +  '<br><b>Distance (m): </b>' + polar_recpts['Distance (m)'] \
                                + '<br><b>Angle (deg): </b>' + polar_recpts['Angle (deg)'] + f'<br><b>{metric}: </b>'\
                                + polar_recpts[metric].apply(lambda x: f'{self.riskfig(x, digz)}').astype(str)
                                                    
                        polarjson = json.loads(polar_recpts.to_json())
                        polarbuf = dlx.geojson_to_geobuf(polarjson)
                        
                    else:
                        polarbuf = None
                        
                    if block_recpts is not None and len(block_recpts) != 0:
                                                
                        if metric == 'MIR':
                            block_recpts['tooltip'] = '<b>Block/User Receptor</b>' + '<br><b>Receptor ID: </b>' + block_recpts['RecID'] \
                                + '<br><b>Cancer Risk (in a million): </b>' + block_recpts[metric].apply(lambda x: f'{self.riskfig(x, digz)}').astype(str)
                        else:
                            block_recpts['tooltip'] = '<b>Block/User Receptor</b>' + '<br><b>Receptor ID: </b>' + block_recpts['RecID'] \
                                + f'<br><b>{metric}: </b>' + block_recpts[metric].apply(lambda x: f'{self.riskfig(x, digz)}').astype(str)
                        blockmax_gdf = block_recpts[block_recpts['Receptor Type'].str.contains('C|P')]
                        block_max_val =  blockmax_gdf[metric].max()
                        if gdf['RecID'].str.contains('UCONC').any():
                            block_recpts_subset = block_recpts.loc[block_recpts['Latitude'].between(lat1, lat2)
                                                                          & block_recpts['Longitude'].between(lon1, lon2)].copy()
                        else:
                            block_recpts_subset = block_recpts
                        
                        blockjson = json.loads(block_recpts_subset.to_json())
                        blockbuf = dlx.geojson_to_geobuf(blockjson)
                                                    
                    else:
                        blockbuf = None                       
                                    
                    ''' Create the meshgrid to which to interpolate
                    '''
                    numcells = round(cont_radius*2*1000/10) 
                    x_coord = np.linspace(lon1, lon2, numcells)
                    y_coord = np.linspace(lat1, lat2, numcells)
                    x_grid, y_grid = np.meshgrid(x_coord, y_coord)
                            
                    ''' Use scipy griddata interpolation on the meshgrid
                    '''
                    # Exclude census blocks/alternate receptors from contours when user-supplied concentration option is used
                    # In this case, the census/alternate receptors are all interpolated and provide no new info
                    if gdf['RecID'].str.contains('UCONC').any():
                        gdf = gdf.loc[gdf['RecID'].str.contains('UCONC')].copy()
                    gdfBounds = gdf.bounds
                    scigrid = griddata((gdfBounds.minx.to_numpy(), gdfBounds.miny.to_numpy()), gdf[metric].to_numpy(),
                                        (x_grid, y_grid), method = 'linear', rescale=True)
                                        
                    minmaxgdf = gdf.loc[gdf['Latitude'].between(lat1, lat2) & gdf['Longitude'].between(lon1, lon2)].copy()
                    
                    # use the scigrid min as datamin unless it is nan
                    # if not gdf['RecID'].str.contains('ang').any() or np.isnan(scigrid.min()):
                    
                    if np.isnan(scigrid.min()):
                        datamin = minmaxgdf[metric].min()
                    else:
                        datamin = scigrid.min()
                    
                    # If there is a block file, use its max value as datamax, unless user has supplied class breaks
                    if usercls is None:
                        if block_max_val is not None:
                            datamax = block_max_val
                        else:
                            datamax = minmaxgdf[metric].max()
                    else:
                        if comp_id == 'ctab-classesdrop':
                            if block_max_val is not None:
                                datamax = block_max_val
                            else:
                                datamax = minmaxgdf[metric].max()
                        else:
                            if block_max_val is not None and len(usercls) == 0:
                                datamax = block_max_val
                            else:
                                datamax = minmaxgdf[metric].max()
                                                                                 
                    # Go thru user class break list, accept only numbers and values within data range
                    finuserlist = []
                    if usercls is None:
                        lowend = datamin
                        highend = datamax
                        # levels = np.linspace(lowend, highend, numclass+1).tolist()
                        levels = np.logspace(np.log10(lowend), np.log10(highend), numclass+1).tolist()
                    else:
                        templist = usercls.split(sep=',')
                        for item in templist:
                            try:
                                if float(item) >= 0:
                                    finuserlist.append(float(item))
                            except:
                                pass
                        
                        for i, item in enumerate(finuserlist):
                            if item > datamax:
                                finuserlist[i] = datamax
                            if item < datamin:
                                finuserlist[i] = datamin
                                
                        finuserlist = sorted(list(set(finuserlist)))
                                      
                    
                        if len(finuserlist) <= 1 or finuserlist[0] > datamax or finuserlist[-1] < datamin or comp_id == 'ctab-classesdrop':
                            lowend = datamin
                            highend = datamax
                            # levels = np.linspace(lowend, highend, numclass+1).tolist()
                            levels = np.logspace(np.log10(lowend), np.log10(highend), numclass+1).tolist()
                        else:
                            if finuserlist[0] < datamin:
                                lowend = datamin
                                finuserlist[0] = lowend
                            else:
                                lowend = finuserlist[0]
                                
                            if finuserlist[-1] > datamax:
                                highend = datamax
                                finuserlist[-1] = highend
                            else:
                                highend = finuserlist[-1]
                            
                            levels = finuserlist
                                                        
                    '''  matplotlib to convert scigrid to filled contours
                    '''
                    fig = plt.figure()        
                    ax = fig.add_subplot(111)
                    gridcontour = ax.contourf(x_coord, y_coord, scigrid, levels=levels, cmap=ramp, norm='log')
                                   
                    '''
                    '''
                    
                    # Using geojsoncontour lib to convert contour to geojson
                    cont_json = geojsoncontour.contourf_to_geojson(
                        contourf=gridcontour,
                        # ndigits=5,
                        unit='',
                        # min_angle_deg = 5
                    ) 
                                                            
                    # # Alternate method to convert contour to geojson
                    
                    # # Extract contour paths and levels
                    # contour_paths = gridcontour.collections
                    # contour_levels = gridcontour.levels
                    
                    # # Convert contour paths to GeoJSON-like format
                    # geojson_data = {
                    #     "type": "FeatureCollection",
                    #     "features": []
                    # }
                    
                    # for i, contour_path in enumerate(contour_paths):
                    #     level = contour_levels[i]
                    #     geojson_feature = {
                    #         "type": "Feature",
                    #         "properties": {"level": level},
                    #         "geometry": {
                    #             "type": "Polygon",
                    #             "coordinates": [contour_path.get_paths()[0].vertices.tolist()]
                    #         }
                    #     }
                    #     geojson_data["features"].append(geojson_feature)
                        
                    # colors = [contour.get_facecolor() for contour in gridcontour.collections]
                    # hex_codes = [matplotlib.colors.to_hex(color) for color in colors]
                    
                    # contgdf = gp.GeoDataFrame.from_features(geojson_data["features"])
                    # contgdf['fill'] = hex_codes
                                        
                    loadcont=json.loads(cont_json)
                    contgdf=gp.GeoDataFrame.from_features(loadcont)
                    classes = levels[:-1]
                    midpts = []
                    for i, level in enumerate(levels[:-1]):
                        midpts.append(roundsf((levels[i] + levels[i+1])/2, digz+2))

                    contgdf['midpts'] = midpts
                                        
                    ctg=[]                               
                    for i, val in enumerate(levels[1:]):
                        
                        if i == 0:
                            ctg.append(f'<b>{self.riskfig(lowend, digz)} - {self.riskfig(val, digz)}</b>')
                        else:
                            levbot = levels[i]
                            ctg.append(f'<b>{self.riskfig(levbot, digz)} - {self.riskfig(val, digz)}</b>')
                            
                    titles = []
                    for i, val in enumerate(levels[1:]):
                        
                        if i == 0:
                            titles.append(f'{self.riskfig(lowend, digz)} - {self.riskfig(val, digz)}')
                        else:
                            levbot = levels[i]
                            titles.append(f'{self.riskfig(levbot, digz)} - {self.riskfig(val, digz)}')
                    
                    contgdf['title'] = titles
                    contgdf.set_crs('epsg:4326')
                    gdfJSON = contgdf.to_json()
                                                            
                    polydata = json.loads(gdfJSON)
                    colorscale = contgdf.fill.to_list()
                    style=dict(weight=1, opacity=1, color='white', fillOpacity=opac)
                                        
                    cont_style = Namespace('HEM_leaflet_functions', 'contour')('draw_contours')
                    draw_blocks = Namespace('HEM_leaflet_functions', 'contour')('draw_block_receptors2')
                    draw_polars = Namespace('HEM_leaflet_functions', 'contour')('draw_polar_receptors2')
                    # draw_cluster = Namespace('HEM_leaflet_functions', 'contour')('draw_cluster')
                    
                    cont_hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp='midpts')
                    
                    # if blockbuf == None and polarbuf != None:
                    #     blocks_or_polars = [dl.Overlay(
                              
                    #             dl.LayerGroup(
                    #             dl.GeoJSON(id = 'ctab-polars', format="geobuf",
                    #                        data=polarbuf,
                    #                        options = dict(pointToLayer=draw_polars),
                    #                        # options = dict(pointToLayer=draw_recepts, onEachFeature=draw_arrow),
                    #                       ),
                    #             ),
                    #             name = 'Polar Receptors', checked = False
                              
                    #       )]
                    # elif polarbuf == None and blockbuf != None:
                    #     blocks_or_polars = [dl.Overlay(
                              
                    #            dl.LayerGroup(
                    #            dl.GeoJSON(id = 'ctab-blocks', format="geobuf",
                    #                       data=blockbuf,
                    #                       # cluster=True, 
                    #                       # superClusterOptions = dict(radius=100),                                                                    
                    #                       options = dict(pointToLayer=draw_blocks),
                    #                       # options = dict(pointToLayer=draw_recepts, onEachFeature=draw_arrow),
                    #                      ),
                    #            ),
                    #            name = 'Block/User Receptors', checked = False
                              
                    #       )]
                    # else:
                    #     blocks_or_polars = [dl.Overlay(
                              
                    #            dl.LayerGroup(
                    #            dl.GeoJSON(id = 'ctab-blocks', format="geobuf",
                    #                       data=blockbuf,
                    #                       # cluster=True, 
                    #                       # superClusterOptions = dict(radius=100),                                                                    
                    #                       options = dict(pointToLayer=draw_blocks),
                    #                       # options = dict(pointToLayer=draw_recepts, onEachFeature=draw_arrow),
                    #                      ),
                    #            ),
                    #            name = 'Block/User Receptors', checked = False
                              
                    #       ),
                       
                    #     dl.Overlay(
                              
                    #            dl.LayerGroup(
                    #            dl.GeoJSON(id = 'ctab-polars', format="geobuf",
                    #                       data=polarbuf,
                    #                       options = dict(pointToLayer=draw_polars),
                    #                       # options = dict(pointToLayer=draw_recepts, onEachFeature=draw_arrow),
                    #                      ),
                    #            ),
                    #            name = 'Polar Receptors', checked = False
                              
                    #       )]
                    
                                    
                    contmap = [
                        
                            dl.MeasureControl(position="topleft", primaryLengthUnit="meters", primaryAreaUnit="hectares",
                                                         activeColor="#214097", completedColor="#972158"),
                        
                            dl.LayersControl([ct_esri, ct_dark, ct_light, ct_openstreet] +
                                             
                                              [ct_roads, ct_places,
                                               
                                               # *blocks_or_polars,
                                                                                                        
                                                   dl.Overlay(
                                                        
                                                          dl.LayerGroup(
                                                          dl.GeoJSON(id = 'ctab-blocks', format="geobuf",
                                                                     data=blockbuf,
                                                                     # cluster=True, 
                                                                     # superClusterOptions = dict(radius=100),                                                                    
                                                                     options = dict(pointToLayer=draw_blocks),
                                                                     # options = dict(pointToLayer=draw_recepts, onEachFeature=draw_arrow),
                                                                    ),
                                                          ),
                                                          name = 'Block/User Receptors', checked = False
                                                        
                                                     ),
                                                 
                                                   dl.Overlay(
                                                        
                                                          dl.LayerGroup(
                                                          dl.GeoJSON(id = 'ctab-polars', format="geobuf",
                                                                     data=polarbuf,
                                                                     options = dict(pointToLayer=draw_polars),
                                                                     # options = dict(pointToLayer=draw_recepts, onEachFeature=draw_arrow),
                                                                    ),
                                                          ),
                                                          name = 'Polar Receptors', checked = False
                                                        
                                                     ),
                                             
                                                 dl.Overlay(
                                                     
                                                     
                                                        dl.LayerGroup(
                                                        dl.GeoJSON(id = 'ctab-contours', format="geojson",
                                                                   data=polydata,
                                                                   options=dict(style=cont_style),
                                                                   zoomToBounds = False,
                                                                   hideout=cont_hideout,
                                                                   ),
                                                        ),
                                                        name = 'Contours', checked = True
                                                        
                                                    ),
                                                 
                                                 # ct_roads, ct_places
                                                                                 
                                             ]
                                             
                                             ),
                                             
                            
                            dl.express.categorical_colorbar(id='thecolorbar', categories= ctg, colorscale= colorscale, width=30,  height = 30*len(levels), opacity = opac,
                                                                position="bottomleft", style = dict(title = metric, title_color= 'black',
                                                                                                    background = 'white', opacity = .9))
                        ]
                    
                    
                    if comp_id in ['ctab-opacdrop','ctab-rampdrop', 'ctab-sigfigdrop', 'ctab-classinput']:
                        center = no_update
                        zoom = no_update
                    else:
                        center = [avglat,avglon]
                        zoom = 14
                    
                    # Close the matplotlib figure
                    plt.close()
                    # return no_update, contmap, maptitle, zoom, center, gdfJSON
                    return no_update, contmap, maptitle, zoom, center, cont_json


        # This callback takes the csv file(s) loaded by user and creates a dataframe
        @app.callback(Output('ctab-store-rawdata', 'data'),
                      Output('ctab-upload-alert-div', 'children'),
                      Output('ctab-store-facid', 'data'),
                      Output('ctab-metricdrop', 'options'),
                      Output('ctab-metricdrop', 'value'),
                                                                        
                      Input('ctab-upload-data', 'filename'),
                      Input('ctab-upload-data', 'contents'),
                      
                      prevent_initial_call=True,
                     )
        
        def store_rawdata(filelist, contents):
                            
            if filelist is None or contents is None:
                alert = no_update
                data = no_update
                facname = no_update
                ddown_opts = no_update
                metric1=no_update
                                                
            else:
                if len(filelist) > 2:
                    alert = self.make_alert("Only load 1 or 2 files")
                    data = no_update
                    facname = no_update
                    ddown_opts = no_update
                    metric1=no_update
                                                                
                else:
                    goodnames = []
                    goodcontents = []
                    for i, name in enumerate(filelist):
                        if 'ring_summary_chronic.csv' in name or 'block_summary_chronic.csv' in name:
                            facname = name.split('_')[0]
                            goodnames.append(name)
                            goodcontents.append(contents[i])
                        else:
                            facname = no_update
                    
                    if len(goodnames) == 0:
                        alert = self.make_alert("No ring or block csv files selected")
                        data = no_update
                        facname = no_update
                        ddown_opts = no_update
                        metric1=no_update
                                                
                    elif len(goodnames) == 2 and (goodnames[0].split('_')[0] != goodnames[1].split('_')[0]):
                        alert =self.make_alert("Facility names for the files don't match")
                        data = no_update
                        facname = no_update
                        ddown_opts = no_update
                        metric1=no_update
                                                        
                    else:
                        dflist =[]
                        for i, item in enumerate(goodnames):
                            # currfile = goodnames[i]
                            currcontent = goodcontents[i]
                            content_type, content_string = currcontent.split(',')
                            decoded = base64.b64decode(content_string)
                            dtype={"FIPs": str, "Block": str, "Receptor ID": str}
                            currdf = pd.read_csv(io.StringIO(decoded.decode('utf-8')), dtype = dtype)
                            currdf.rename(columns={'Distance (m)': 'dist', 'Angle (from north)': 'angle'}, inplace=True)
                            
                            if 'angle' in currdf.columns:
                                currdf['RecID'] = currdf.dist.astype(str).str.cat(currdf.angle.astype(str), sep='ang')
                                currdf['Receptor Type'] = 'R'
                            elif 'Receptor ID' in currdf.columns:
                                currdf['RecID'] = currdf['Receptor ID']            
                            else:
                                currdf['RecID'] = currdf.FIPs.astype(str).str.cat(currdf.Block.astype(str))
                                                        
                            tempdf = currdf.copy()
                            tempdf['MIR'] = tempdf['MIR']*1000000
                            
                            # Limit the number of block receptors (don't need so many nor so far out)
                            if 'block_summary_chronic.csv' in item and ~currdf['RecID'].str.contains('UCONC', case=False, na=False).any():
                                                                    
                                try:
                                    for metric in metrics.values():
                                        if tempdf[metric].max() == 0:
                                            pass
                                        else:
                                            maxid = tempdf[metric].idxmax()
                                            midlat = tempdf.loc[maxid, 'Latitude']
                                            midlon = tempdf.loc[maxid, 'Longitude']
                                            break
                                
                                except:
                                    midlat = (tempdf['Latitude'].max() + tempdf['Latitude'].min())/2
                                    midlon = (tempdf['Longitude'].max() + tempdf['Longitude'].min())/2
                                    
                                grab_radius = 10 # only get blocks within 10km of center
                                r_earth = 6371
                                fac_center = [midlon, midlat]
                                lat2 = fac_center[1]  + (grab_radius / r_earth) * (180 / pi)
                                lon2 = fac_center[0] + (grab_radius / r_earth) * (180 / pi) / cos(np.deg2rad(fac_center[1]))
                                lat1 = fac_center[1]  - (grab_radius / r_earth) * (180 / pi)
                                lon1 = fac_center[0] - (grab_radius / r_earth) * (180 / pi) / cos(np.deg2rad(fac_center[1]))
                                tempdf = tempdf.loc[tempdf['Latitude'].between(lat1, lat2) & tempdf['Longitude'].between(lon1, lon2)].copy()
                                             
                            dflist.append(tempdf)
                           
                            
                        alldfs = pd.concat(dflist)
                                                
                        # Find all risk metric columns with at least one nonzero value
                        nonzero_columns = alldfs.columns[alldfs.apply(lambda x: x != 0).any()]
                        nonzero_metrics = list(nonzero_columns.intersection(list(metrics.values())))
                        nz_metrics_dict = {key: metrics_reversed.get(key, None) for key in nonzero_metrics}
                        nz_metrics_rev = {value: key for key, value in nz_metrics_dict.items()}
                        ddown_opts = [{"label": key, "value": value} for key, value in nz_metrics_rev.items()]
                        metric1=ddown_opts[0]['value']
                                                                                     
                        alert=no_update
                        data = alldfs.to_dict('records')
                                        
                return data, alert, facname, ddown_opts,metric1
                
                
        # Take the df of the concatenated raw data and trim down the columns to chosen metric               
        @app.callback(Output('ctab-store-metricdata', 'data'),
                                                  
                      Input('ctab-store-rawdata', 'data'),
                      Input('ctab-metricdrop', 'value'),
                      
                      prevent_initial_call=True,
                  )            
        def send_metdata(indata, metric):
            if indata is None:
                return no_update
            else:
                ctx = callback_context
                comp_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if comp_id is None or comp_id not in ['ctab-store-rawdata', 'ctab-metricdrop']:
                    return no_update
                else:
                    dff = pd.DataFrame(indata)
                    dff2 = dff.loc[:,['RecID', 'Latitude', 'Longitude', metric, 'Receptor Type']]
                           
                    outdata = dff2.to_dict('records')
                    return outdata

            
        @app.callback(            
                Output("ctab-offcanvas0", "is_open"),

                Input("ctab-open-offcanvas0", "n_clicks"),
                State("ctab-offcanvas0", "is_open")
                )
        def toggle_offcanvas0(n1, is_open):
            if n1:
                return not is_open
            return is_open    
    
        @app.callback(            
                Output("modal", "is_open"),
                Input("modalbutton", "n_clicks"),
                State("modal", "is_open")
                )
        def toggle_modal(n1, is_open):
            if n1:
                return not is_open
            return is_open
        
        # Callback to send geojson to dcc download
        @app.callback(
                Output("download-cont-geojson", "data"),
                Input("download-json-button", "n_clicks"),
                Input('ctab-store-cont-json', 'data'),
                Input('ctab-store-facid', 'data'),
                                
                prevent_initial_call=True,
            )
        def send_json(n_clicks, geojson_data, fac):
            return dict(content=geojson_data, filename=f'{fac}_contours.geojson')
                        
        # # Callback to send shapefile to dcc download
        # @app.callback(
        #         Output("download-cont-shapefile", "data"),
        #         Input("download-shapefile-button", "n_clicks"),
        #         Input('ctab-store-cont-json', 'data'),
        #         Input('ctab-store-facid', 'data'),
                                
        #         prevent_initial_call=True,
        #     )
        # def send_shape(n_clicks, geojson_data, fac):
        #     gdf = gp.read_file(geojson_data)
        #     shapefile_path = f'{fac}_contours.shp'
        #     gdf.to_file(shapefile_path, driver="ESRI Shapefile")
        #     # Read the Shapefile as bytes
        #     with open(shapefile_path, "rb") as file:
        #         shapefile_data = file.read()
                
        #     os.remove(shapefile_path)
            
        #     return dcc.send_bytes(shapefile_data, filename=f'{fac}_shapefile.zip')
        
        # Callbacks to send the map footer
        @app.callback(
                   Output('block-footer', 'children'),
                                     
                  Input('ctab-store-metricdata', 'data'),
                  Input('ctab-metricdrop','value'),
                  Input('ctab-sigfigdrop', 'value')                                   
                  ) 
        
        def send_footer(metdata, metric, digz):
            if metdata is None:
                return no_update
            else:
                tempdf = pd.DataFrame(metdata)
                block_data = tempdf[tempdf['Receptor Type'].str.contains('C|P') &
                                    ~tempdf['RecID'].str.contains('UCONC')]
                if len(block_data)==0:
                    return None
                else:
                    maxrisk = block_data[metric].max()
                    maxrisk_sf = self.riskfig(maxrisk, digz)
                    
                    if tempdf['RecID'].str.contains('UCONC').any():
                        return html.P(f'** Census block/alternate receptors are included out to 20km from the location of maximum impact.\
                                      The maximum {metrics_reversed[metric]} for a populated receptor is {maxrisk_sf} based on your input data.')
                    else:
                        return html.P(f'** Census block/alternate receptors are included out to 10km from the location of maximum impact.\
                                  The maximum {metrics_reversed[metric]} for a populated receptor is {maxrisk_sf} based on your input data.')
                                  
                    
                            
        return app

 

    def shutdown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        time.sleep(20)
        func()
