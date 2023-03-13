# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 13:28:34 2022

@author: mmorr
"""
import pandas as pd
from sigfig import round as roundsf

from dash import html, no_update, dcc
from dash_extensions.javascript import assign, arrow_function
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from hem_leaflet import get_basemaps


metrics = ['MIR', 'Respiratory HI', 'Liver HI', 'Neurological HI',
'Developmental HI', 'Reproductive HI', 'Kidney HI', 'Ocular HI',
'Endocrine HI', 'Hematological HI', 'Immunological HI', 'Skeletal HI',
'Spleen HI', 'Thyroid HI', 'Whole body HI']

coloramps = ['viridis', 'magma', 'cividis', 'rainbow', 'gist_earth','terrain','jet', 'turbo',
             'ocean', 'tab10',
             'Blues', 'Greens', 'Oranges', 'Reds',
             'viridis_r', 'magma_r', 'cividis_r', 'rainbow_r', 'gist_earth_r','terrain_r','jet_r', 'turbo_r',
             'ocean_r', 'tab10_r',
             'Blues_r', 'Greens_r', 'Oranges_r', 'Reds_r']

draw_hoverfac = assign("""function(feature, latlng){
    const square = L.icon({iconUrl: `/assets/greensquare.png`, iconSize: [10, 10]});
    
    return L.marker(latlng, {icon: square});
    }""")
    
draw_arrow = assign("""
function(feature, layer, context){
    const map = context.myRef.current.leafletElement._map;
    L.polylineDecorator(layer, {
          patterns: [
              {symbol: L.Symbol.arrowHead({pixelSize: 15, pathOptions: {fillOpacity: 1, weight: 2}})}
          ]
    }).addTo(map);}
""")
    
# draw_label = assign("""function(feature, layer) {
#         layer.bindLabel(feature.properties.[colrProp]);
#     }""") 

style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
    return style;
}""")
bases = get_basemaps()    
ct_esri = bases[0]
ct_dark = bases[1]
ct_light = bases[2]
ct_openstreet = bases[3]
ct_roads = bases[4]
 # esri, dark, light, openstreet, roads = get_basemaps()
 
markers = [dl.Marker(position=[56, 10]), dl.CircleMarker(center=[55, 10])]
    
def make_alert(string):
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
    
def riskfig(numb, digz):
    numtype = float if numb < 1 else int
    return roundsf(numb,sigfigs = digz, output_type = numtype)

def make_contours():
    
    cont_tab = dbc.Container([
            
                    dcc.Store(id='ctab-store-rawdata'),
                    dcc.Store(id='ctab-store-metricdata'),
                    dcc.Store(id='ctab-store-facid'),
                            
                    dbc.Row([
                        
                        dbc.Col([
                            dcc.Loading([
                                
                                html.Div([
                                    html.H4('Select files to create contours')
                                    ], id='ctab-map-title')
                                
                                ], type = 'default')
                           
                                
                            ], width={'size':8, 'offset':2})
                        
                        ]),
            
                    dbc.Row([
                        
                        dbc.Col([
                            
                            dcc.Upload(['Select File(s)'],
                                
                                       id='ctab-upload-data',
                                       multiple = True,
                                       accept = '.csv',
                                       style={
                                           
                                            'width': '100%',
                                            'height': '60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '2px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center'
                                        }),
                            
                            html.Div(id='ctab-upload-alert-div'),
                                                                   
                            dbc.Tooltip(                        
                                [html.P('Select ring summary and/or block summary files'),
                                html.P('Found in C:\HEMX.Y\output\<your model run group>\<facility ID>')],
                                target='ctab-upload-data',
                                class_name="fw-bold"
                            ),
                            
                            html.Br(),
                            html.Label(["Risk metric"]),
                            dcc.Dropdown(id='ctab-metricdrop',
                                          options=[{"label": i, "value": i} for i in metrics],
                                          multi=False,
                                          clearable=False,
                                          value = 'MIR',
                                          placeholder="Select a Metric",
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
                                 html.P('Press enter after you input', style={'font-weight':'bold', 'font-style':'italic' })],
                                target='ctab-classinput',
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
                                                
                            html.Hr(),
                            html.Label(["Opacity"]),
                            dcc.Slider(.1, 1, .1,
                                       value=.8,
                                       marks=None,
                                       id='ctab-opacdrop'
                                       ),
                            
                            html.Hr(),
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
                                                            html.Label(["Download contours as shapefile"]),
                                                            
                                                            html.Label(["Download receptor data as csv file"]),
                                                            
                                                                                                                                                        
                                                            ], width = 12, className="opacity-100"),
                                                    
                                                            
                                            ], className="opacity-100"),    
                                            
                                            id="ctab-offcanvas0",
                                            is_open=False,
                                        ),
                                                        
                            ], width = 2),
            
                        
                        dbc.Col([
                                                                                        
                                dl.Map(id = 'ctab-themap', center = [39., -97.3],
                                       zoom=5, children=[
                                           dl.MeasureControl(position="topleft", primaryLengthUnit="meters", primaryAreaUnit="hectares",
                                                                        activeColor="#214097", completedColor="#972158"),
                                           dl.LayersControl([ct_esri, ct_dark, ct_light, ct_openstreet] +
                                                            
                                                            [dl.Overlay(dl.LayerGroup(markers), name="markers", checked=True),
                                                             
                                                             ct_roads]
                                                            
                                                            ),
                                          
                                           ]),
                                                                        
                                ], width=10)
                                                 
                    ], className="h-100")
                
            ], fluid=True, style={"height": "90vh"})
        
                                    
    return cont_tab





