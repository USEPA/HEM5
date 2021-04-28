# -*- coding: utf-8 -*-

import fnmatch
import os
import pandas as pd
import numpy as np

import plotly
import plotly.express as px
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import traceback
from threading import Timer
import webbrowser
from flask import request
import time
import tkinter as tk


class EJdash():

    def __init__(self, dirtouse):
        self.dir = dirtouse
        self.SCname = os.path.split(self.dir)[1]

    def buildApp(self):
    
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        
        mapbox_access_token = 'pk.eyJ1IjoiYnJ1enp5IiwiYSI6ImNrOTE5YmwzdDBhMXYzbW8yMjY4aWJ3eHQifQ.5tNjnlK2Y8b-U1kvfPP8FA'
        px.set_mapbox_access_token(mapbox_access_token)
        #pd.set_option("display.max_columns", 50)
        #pd.options.display.max_colwidth = 50
                
        ##### Get max risk and HI file and create a dataframe for the map
        fname = self.SCname + '_facility_max_risk_and_hi.xlsx'
        maxfile = os.path.join(self.dir, fname)
        usecols = [0,1,6,7,13,17,23,27,31,35,39,43,47,51,55,59,68,71,72]
        names = ['Facility', 'mx_can_rsk', 'Block ID', 'Respiratory HI', 'Liver HI', 'Neurological HI', 'Developmental HI',
                 'Reproductive HI', 'Kidney HI', 'Ocular HI', 'Endocrine HI', 'Hematological HI', 'Immunological HI',
                 'Skeletal HI', 'Spleen HI', 'Thyroid HI', 'Cancer Incidence', 'Latitude', 'Longitude']
        datatypes = {'Facility': str, 'Block ID': str}
        
        xlsheet = pd.read_excel(maxfile, usecols=usecols, names=names, dtype=datatypes)
        xlsheet['MIR (in a million)']= xlsheet['mx_can_rsk']*1000000
        mapmets = ['MIR (in a million)', 'Respiratory HI', 'Liver HI', 'Neurological HI', 'Developmental HI',
                 'Reproductive HI', 'Kidney HI', 'Ocular HI', 'Endocrine HI', 'Hematological HI', 'Immunological HI',
                 'Skeletal HI', 'Spleen HI', 'Thyroid HI']
        
        ##### Get EJ summary files
        pattern_list = ["*Summary*"]
        ejdir = os.path.join(self.dir, 'ej')
        files = os.listdir(ejdir)
        for pattern in pattern_list:
            file_list = fnmatch.filter(files, pattern)
        
        rungroup = file_list[0].split('_')[0]
        extension = file_list[0].split('_')[5]
        demogroups = ['Minority', 'African American','Native American', 'Other and Multiracial', 'Hispanic or Latino',
                      'Age 0-17', 'Age 18-64', 'Age >=65','Below the Poverty Level', 'Over 25 Without a High School Diploma',
                      'Linguistically Isolated']
        
        ### Go through the files (and sheets within files) to get all the scenarios run in the Community Assessment module
        scenarios = pd.DataFrame(columns = ['Metric', 'Distance', 'Risk_Level', 'Filename'])
        scen_ind = 0
        
        for file in file_list:
                metric = file.split('_')[4]
                distance = file.split('_')[2]
                fname = os.path.join(ejdir, file)
                xl = pd.ExcelFile(fname)
                RHI = xl.sheet_names
                RHI_prox = xl.sheet_names + ['Proximity Only']
        
                for sheet in RHI_prox:
                    scenarios.loc[scen_ind, 'Metric'] = metric
                    scenarios.loc[scen_ind, 'Distance'] = distance
                    scenarios.loc[scen_ind, 'Risk_Level'] = sheet
                    fname = os.path.join(ejdir, rungroup + '_EJ-Summary_' + distance + '_km_' + metric + '_' + extension)
                    scenarios.loc[scen_ind, 'Filename'] = fname
                    scen_ind +=1
        
        metrics = scenarios['Metric'].unique()
        
        ### Create a dataframe of the national, state, and county averages
        compnames = ['Average', 'Total Pop', 'Minority', 'African American','Native American',
                     'Other and Multiracial', 'Hispanic or Latino','Age 0-17', 'Age 18-64', 'Age >=65',
                     'Below the Poverty Level', 'Over 25 Without a High School Diploma','Linguistically Isolated']
        compdf = pd.DataFrame()
        
        for scen in scenarios.itertuples():
            temp = pd.read_excel(scen.Filename, skiprows = [0,1], usecols = [0, 2,3,4,5,6,7,8,9,10,11,12,13],
                                 names = compnames
                                 )
            compdata = temp.loc[temp['Average'].isin(['Nationwide', 'State', 'County'])]
            compdata['Distance'] = scen.Distance
            compdf = compdf.append(compdata)
        
        compdf.drop_duplicates(inplace = True)
        
        ### Create a dataframe of the facility data        
        mainnames = ['Facility', 'RiskorProx', 'Total Pop', 'Minority', 'African American','Native American',
                     'Other and Multiracial', 'Hispanic or Latino','Age 0-17', 'Age 18-64', 'Age >=65',
                     'Below the Poverty Level', 'Over 25 Without a High School Diploma','Linguistically Isolated']        
        maindf = pd.DataFrame()
        noprox = scenarios[~scenarios['Risk_Level'].isin(['Proximity Only'])]
        
        for file in file_list:
            fname = os.path.join(ejdir, file)
            xl = pd.ExcelFile(fname)
            sheets = xl.sheet_names
            for sheet in sheets:
        
                temp = xl.parse(skiprows = [0,1,3,4,5,6,7,8,9], names = mainnames)
                temp.insert(0, 'Metric', file.split('_')[4])
                temp.insert(1, 'Distance', file.split('_')[2])
                temp.insert(2, 'Risk_Level', sheet)
                
                ## Adding cols for demog group pop; and facility names in rows where absent
                for i, row in temp.iterrows():
                    for col in demogroups:
                        newcol = col + ' Pop'
                        temp[newcol] = (temp[col] * temp['Total Pop'])
                                                                 
                    if pd.isna(row[3]):
                        temp.iat[i,3] = temp.iat[i-1,3]
                
                # Convert the decimal fractions to percents for the demo groups        
                for col in demogroups:
                    temp[col] = 100 * temp[col]
                
                maindf = maindf.append(temp, ignore_index = True)
        
        
        ##### The app layout 
        app.layout = html.Div([
            
                #Shutdown
                dcc.Input(id="input1", type="hidden", value="shutdown"),
                dcc.Input(id="input2", type="hidden"),

                html.Div([
                        html.H1("Community Assessment for HEM4 Run Group " + rungroup, style={'text-align':'left', 'font-weight': 'bold'}),
                        html.Button('Click here to add another run group', id='dirbutton'),
                        html.Br(),
                        html.Br(),
                        ], className = 'row'),
                
                html.H3(id='button-clicks'),
                html.Hr(),
                            
                dcc.Tabs([
                        dcc.Tab(label="Bar Graph",children=[
        
                            
                                ###########  Start Chart Dropdowns  ##########
                                
                                html.Div([
                                    
                                    html.Div([html.H6("Risk Metric"),
                                             dcc.Dropdown(id='riskdrop',
                                                          
                                                          options=[{"label": i, "value": i} for i in metrics],
                                                          multi=False,
                                                          clearable=True,
                                                          value = scenarios.loc[0, 'Metric'],
                                                          placeholder="Select a Metric",
                                                          ),
                                            ], className = 'two columns'),
                                             
                                    html.Div([html.H6("Distance (km)"),
                                              dcc.Dropdown(id='distdrop',             
                                                          multi=False,
                                                          clearable=True,
                                                          value = scenarios.loc[0, 'Distance'],
                                                          placeholder="Select a Distance (km)",
                                                          ),
                                            ], className = 'two columns'),
                                    
                                    html.Div([html.H6("Risk/HI Level"),
                                              dcc.Dropdown(id='leveldrop',
                                                          multi=False,
                                                          clearable=True,
                                                          value = scenarios.loc[0, 'Risk_Level'],
                                                          placeholder="Select a Risk or HI Level",
                                                          ),
                                            ], className = 'two columns'),
                                                           
                                    html.Div([html.H6("Demographic Group"),
                                              dcc.Dropdown(id='demodrop',
                                                           
                                                          options=[{"label": i, "value": i} for i in demogroups],
                                                          multi=False,
                                                          clearable=True,
                                                          value = 'Minority',
                                                          placeholder= 'Select a Demographic Group',
                                                          ),
                                            ], className = 'two columns'),
                                    
                                    html.Div([html.H6("Bar Heights: % or Pop"),
                                              dcc.Dropdown(id='barhtdrop',
                                                           
                                                          options=[{"label": '%', "value": 'Pct'},
                                                                   {"label": 'Population', "value": 'Pop'}
                                                                   ],
                                                          multi=False,
                                                          clearable=False,
                                                          value = 'Pct',
                                                          placeholder="% or Population",
                                                          ),
                                            ], className = 'two columns'),
                                    
                                    html.Div([html.H6("Sort by % or Pop"),
                                              dcc.Dropdown(id='sortdrop',
                                                           
                                                          options=[{"label": '%', "value": 'Pct'},
                                                                   {"label": 'Population', "value": 'Pop'}
                                                                   ],
                                                          multi=False,
                                                          clearable=False,
                                                          value = 'Pct',
                                                          placeholder="% or Population",
                                                          ),
                                            ], className = 'two columns')
                                          
                                ], className = 'row'),
                                
                                html.Div([
                                        html.Hr(),
                                        ], className = 'row'),
                                
                                ###########  End Chart Dropdowns  ##########
                             
                                    
                                html.Div([
                                        dcc.Graph(id = 'barchart', config = 
                                                  {'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'hoverCompareCartesian', 'hoverClosestCartesian'],
                                                   'toImageButtonOptions': {
                                                           'format': 'jpeg', # one of png, svg, jpeg, webp
                                                          'filename': 'Demographics Bar Chart',
                                                          'scale': 1}
                                                  }),
                                        html.Hr()
                                        ], className='twelve columns'),
            
                        ]),
                
                        dcc.Tab(label="Map of Facilities",children=[
                                
                                
                                            ###########  Start Map Dropdowns  ##########
        
                                html.Div([
                                        
                                        html.H6("Metric to Display"),
                                          dcc.Dropdown(id='metdrop',
                                                       
                                                      options=[{"label": i, "value": i} for i in mapmets],
                                                      multi=False,
                                                      clearable=False,
                                                      value = 'MIR (in a million)',
                                                      placeholder="Select a Metric",
                                                      ),
                                        
                                        html.H6("Linear or Log Scale"),
                                          dcc.Dropdown(id='scaledrop',
                                                       
                                                      options=[{"label": 'Linear', "value": 'linear'},
                                                               {"label": 'Log', "value": 'log'}
                                                               ],
                                                      multi=False,
                                                      clearable=False,
                                                      value = 'linear',
                                                      placeholder="Linear or Log Scale",
                                                      ),
                                        
                                                        
                                        html.H6("Basemap"),
                                          dcc.Dropdown(id='basemapdrop',
                                                       
                                                      options=[{"label": 'Light', "value": 'carto-positron'},
                                                               {"label": 'Dark', "value": 'carto-darkmatter'},
                                                               {"label": 'Satellite', "value": 'satellite-streets'},
                                                               {"label": 'Streets', "value": 'open-street-map'}
                                                               ],
                                                      multi=False,
                                                      clearable=False,
                                                      value = 'carto-positron',
                                                      placeholder="Select a Basemap",
                                                      ),
                                  
                                        html.H6("Color Ramp"),  
                                          dcc.Dropdown(id='rampdrop',
                                                       
                                                      options=[{"label": 'Blue to Red', "value": px.colors.sequential.Bluered},
                                                               {"label": 'Purple to Yellow', "value": px.colors.sequential.Viridis},
                                                               {"label": 'Green Scale', "value": px.colors.sequential.Greens},
                                                               {"label": 'Red Scale', "value": px.colors.sequential.Reds}],
                                                      multi=False,
                                                      clearable=False,
                                                      value = px.colors.sequential.Viridis,
                                                      placeholder="Select a Color Ramp",
                                                      ),
                                                       
                                        html.H6("Dot Size"),  
                                          dcc.Dropdown(id='sizedrop',
                                                       
                                                      options=[{"label": i, "value": i} for i in range(5,16)],
                                                      multi=False,
                                                      clearable=False,
                                                      value = 6,
                                                      placeholder="Select a Dot Size",
                                                      ),
                                ], className = 'two columns'),
                                              
                                html.Div([
                                    
                        
                                    html.Div([
                                        dcc.Graph(id = 'map', style={"height": 800}, config = {
                                                'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'hoverCompareCartesian', 'hoverClosestCartesian'],
                                                'toImageButtonOptions': {
                                                        'format': 'jpeg', # one of png, svg, jpeg, webp
                                                        'filename': 'Facility Map',
                                                        'scale': 1}
                                                  }),
                                    ], className='ten columns'),
                        
                                        
                                ], className = 'row'),
                                       
                        ]),
                                                       
                        dcc.Tab(label="Summary Table",children=[
                                                     
                                       
                                dash_table.DataTable(
                                        id='table',
                                        columns=[
                                                {"name": ['Scenario', 'Metric'], "id": 'Metric'},
                                                {"name": ['Scenario', 'Distance (km)'], "id": 'Distance (km)'},
                                                {"name": ['Scenario', 'Risk Level'], "id": 'Risk Level'},
                                                {"name": ['Scenario', 'Total Facility Count'], "id": 'Total Facility Count'},
                                                {"name": ['', 'Average'], "id": 'Average'},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'Minority'], "id": 'Minority'},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'African American'], "id": 'African American'},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'Native American'], "id": 'Native American'},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'Other and Multiracial'], "id": 'Other and Multiracial'},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'Hispanic or Latino'], "id": 'Hispanic or Latino'},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'Age 0-17'], "id": 'Age 0-17'},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'Age 18-64'], "id": 'Age 18-64'},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'Age >=65'], "id": 'Age >=65'},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'Below the Poverty Level'], "id": 'Below the Poverty Level'},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'Over 25 Without a High School Diploma',], "id": 'Over 25 Without a High School Diploma',},
                                                {"name": ['Number (or %) of Facilities Exceeding the Geographic Average', 'Linguistically Isolated'], "id": 'Linguistically Isolated'}
                                                
                                        ],
                                        merge_duplicate_headers=True,
                                        data=[],
                                        page_action='none',     # render all of the data at once
                                        style_table={'height': '800px', 'width': '100%', 'overflowY': 'auto'},
                                        fixed_rows={"headers": True},
                                        export_format = 'xlsx',
                                        style_header={
                                                'backgroundColor': 'LightGrey',
                                                'fontWeight': 'bold',
                                                'fontSize':16,
                                                'border': '1px solid black',
                                                'textAlign': 'center'
                                                },
        #                                style_as_list_view=True,        
                                        style_cell={
                                                'whiteSpace': 'normal',
                                                'height': 'auto',
                                                'font-family': 'verdana',
                                                'fontSize':15,
                                                'minWidth': '10px', 'width': '110px', 'maxWidth': '200px'},
                                        style_cell_conditional=[
                                                {'if': {'column_id': 'Metric'},'width': '5%'},
                                                {'if': {'column_id': 'Distance (km)'},'width': '5%'},
                                                {'if': {'column_id': 'Total Facility Count'},'width': '5%'},
                                                {'if': {'column_id': 'Average'},'width': '5%'},
                                                {'if': {'column_id': 'Risk Level'},'width': '8%'},
                                                {'if': {'row_index': [3,4,5,9,10,11,15,16,17,21,22,23,27,28,29,33,34,35,39,40,41]},
                                                 'backgroundColor': '#F7D8F4'
                                                },
        
                                        ],
                                                        
                                        ),
                                
                                html.Hr(),                         
                                       
                                html.Div([
                                        html.H6("Choose a percentage above the geographic averages to get the number (or %) of facilities above that level",
                                                style={'text-align':'center', 'font-weight': 'bold'},
                                                className = 'eight columns'),
                                        dcc.Slider(                     
                                                id='my-slider',
                                                min=0,
                                                max=100,
                                                step=5,
                                                value=0,
                                                marks={i: '{}%'.format(i) for i in range(0,110,10)},
                                                className = 'eight columns'
                                                ),
                                                                        
                                        dcc.RadioItems(id = 'radio',                                        
                                                options=[
                                                    {'label': 'Show Number of Facilities', 'value': 'num'},
                                                    {'label': 'Show Percentage of Facilities', 'value': 'pct'}
                                                ],
                                                value='num',
                                                labelStyle={'display': 'inline-block'},
                                                className = 'two columns'
                                            ),
                                 
                                ]),
                                                     
                        ]),
                                        
                        dcc.Tab(label='Learn More',children=[
                                html.H2('About the Bar Graph'),
                                html.H3('Risk Metrics'),
                                html.Div('''Information about risk metrics'''),
                                html.H3('Distance'),
                                html.Div('''Information about distance'''),
                                html.H3('Risk/HI Level'),
                                html.Div('''Information about risk/HI level'''),
                                html.H3('Demographic Groups'),
                                html.Div('''Information about demographic groups'''),
                                html.H3('Bar Heights and Sorting'),
                                html.Div('''Information about bar heights and sorting'''),
                                html.H3('Other Graph Features'),
                                html.Div('''Other relevant information about the graph; for example, mentioning that each bar represents a single facility, and the horizontal pink bar represents county, state, and national average levels for the group/metric/level in question.'''),
                                html.Hr(),
                                html.H2('About the Map'),
                                html.H3('Metric to Display'),
                                html.Div('''Information about metrics to display (MIR, Respiratory HI, etc.)'''),
                                html.H3('Scale'),
                                html.Div('''Quick explanation of the differences between linear and log scales'''),
                                html.H3('Basemap'),
                                html.Div('''Description of each of the basemaps available (light, dark, etc.)'''),
                                html.H3('Color Ramp'),
                                html.Div('''Description of each of the color ramps available (yellow to purple, blue to red, etc.)'''),
                                html.H3('Dot Size'),
                                html.Div('''Quick explanation of what dot size means'''),
                                html.H3('Other Map Features'),
                                html.Div('''Other relevant information about the map and what is displayed.'''),
                                html.Hr(),
                                html.H2('About the Summary Table'),
                                html.H3('Scenarios'),
                                html.Div('''Explanation that these columns collectively describe the combination of factors that contribute to determining how many/what percentage of facilities exceed the various averages, as shown in the table (but worded better than what I wrote)'''),
                                html.H4('Metric'),
                                html.Div('''Definitions of metrics - in the data I'm looking at, it's just cancer'''),
                                html.H4('Distance'),
                                html.Div('''Explanation of 50 vs 5 vs other distances'''),
                                html.H4('Risk Level'),
                                html.Div('''Definitions of terms like Proximity Only or the other risk levels (1/1 million, 50/1 million, etc)'''),
                                html.H4('Total Facility Count'),
                                html.Div('''Explanation that this shows how many facilities fall under the scenario described by the metric, distance, and risk level shown'''),
                                html.H3('Average'),
                                html.Div('''Explanation of nationwide vs state vs county terms and that this table compares the facility risk levels to those respective averages'''),
                                html.H3('Demographic Groups'),
                                html.Div('''Definitions (pulled straight from HEM4 guide) for Minority, African American, Native American, Other and Multiracial, Hispanic or Latino, Age 0-17, Age 18-64, Age >= 65, Below the Poverty Level, Over 25 Without a High School Diploma, andLinguistically Isolated'''),
                                html.H3('Sliding Scale'),
                                html.Div('''Explanation of sliding scale and the option to show the number of facilities vs the percentage of facilities in the table'''),
                                html.Hr(),
                                html.H2('About HEM4'),
                                html.Div('''Probably pulled straight from HEM4 guide. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'''),
                                html.Hr(),
                                ]),
                                        
                ]),
        
                              
        ])
 
        ##############################
        ##  Callbacks
        ##############################
                          
                          
        ### Callback for the Distance Dropdown                  
        @app.callback(Output('distdrop', 'options'),
                      [Input('riskdrop', 'value'),
                       Input('leveldrop', 'value')]
                       )
        def distlist(metric, level):
            if None in [metric, level]:
                pass
            else:
                shortlist = scenarios.loc[scenarios['Metric'] == metric]['Distance'].unique()
                options = [{"label": i, "value": i} for i in shortlist]
        
                return options                 
                          
        ### Callback for the Risk Level Dropdown                  
        @app.callback(Output('leveldrop', 'options'),
                      [Input('riskdrop', 'value'),
                       Input('distdrop', 'value')]
                       )
        def levellist(metric, distance):
            if None in [metric, distance]:
                pass
            else:
                shortlist = scenarios.loc[(scenarios['Distance'] == distance) & (scenarios['Metric'] == metric)]['Risk_Level'].unique()
                options = [{"label": i, "value": i} for i in shortlist]
        
                return options                   
        
        ### Callback for the Bar Chart
        @app.callback(Output('barchart', 'figure'),
                     [Input('riskdrop', 'value'),
                      Input('distdrop', 'value'),
                      Input('leveldrop', 'value'),
                      Input('demodrop', 'value'),
                      Input('barhtdrop', 'value'),
                      Input('sortdrop', 'value')
                     ])
        def makebar (risk, distance, level, group,barht, sort):
            if None in (risk,distance,level,group):
                pass
            else:
                if level == 'Proximity Only':
                    dff = maindf.loc[(maindf['Metric'] == risk) & (maindf['Distance'] == distance) & (maindf['RiskorProx'] == 'Proximity')]
                else:
                    dff = maindf.loc[(maindf['Metric'] == risk) & (maindf['Distance'] == distance) & (maindf['Risk_Level'] == level) &
                                     (maindf['RiskorProx'] != 'Proximity')]
                
                if sort == 'Pct':
                    sorter = group
                else:
                    sorter = group + ' Pop'
                
                dff = dff.loc[(dff[group] > 0) & (dff[group + ' Pop'] >= 1)].sort_values(by=[sorter], ascending = False)
                
                dff = dff.round(decimals = 1)
                
                ### Get the geographic averages for the given distance and demographic group
                natwide = compdf.loc[(compdf['Average'] == 'Nationwide') & (compdf['Distance'] == distance), group]
                statwide = compdf.loc[(compdf['Average'] == 'State') & (compdf['Distance'] == distance), group]
                countwide = compdf.loc[(compdf['Average'] == 'County') & (compdf['Distance'] == distance), group]
                natwide = round(natwide[0]*100,1)
                statwide = round(statwide[1]*100,1)
                countwide = round(countwide[2]*100,1)
                
                ### Set chart title based on user choice of proximity or risk        
                if level == 'Proximity Only':
                    title = '<b>Demographics for ' + risk + ' for Radius ' + distance + ' km (Proximity Only)</b>'
                    
                else:
                    title = '<b>Demographics for ' + risk + ' for Radius ' + distance + ' km (' + level +')</b>'
                    
                numFacs = (dff['Facility'].count())
                
                ### Set chart axes and axes titles based on user choices
                if barht == 'Pop':
                    yaxis = group + ' Pop'
                    text = group
                    texttemplate = '%{text:.0f}%'
                    ytitle = '<b>' + group + ' Population</b>'
                    type = 'log'
                    
                else:
                    yaxis = group
                    text = group +' Pop'
                    texttemplate = '%{text:,.0f}'
                    ytitle = '<b>' + group + ' (%)</b>'
                    type = 'linear'
                
                fig = px.bar(dff, x='Facility', y=yaxis, height=800, width=1500, text = text,opacity=.7)
                fig.update_yaxes(type = type, title_text=ytitle, title_font=dict(size = 16, color = 'black'))
                fig.update_xaxes(title_text='<b>Facility</b>', title_font=dict(size = 16, color = 'black'), tickangle=40,
                                 type = 'category', range = (-.5, min(numFacs,50)))
                fig.update_layout(title = title, title_font=dict(size = 22, color = 'black'),
                                  clickmode="event+select", hovermode = 'closest')
                fig.update_traces(texttemplate=texttemplate)
                
                stats = [natwide,statwide,countwide]
                label = "<b>Nation: {}<br> State: {}<br> County: {}</b>".format(natwide, statwide, countwide)
                   
                ### Add national, state, and county averages, but only for percentage plots 
                if barht == 'Pct':
                    
                    if min(stats) == max(stats):
                        ymax = max(stats)+1
                    else:
                        ymax = max(stats)
                                
                    fig.add_shape(                                        
                                type = 'rect',
                                layer = 'below',
                                yref = 'y', y0 = min(stats), y1 = ymax,
                                xref = 'paper', x0 = 0, x1 = 1,
                                line=dict(color="plum", width=0),
                                fillcolor="plum",
                                opacity = .5
                    )
                                
                    annotations = [dict(xref = 'paper', x = 1,
                                        y = (min(stats) + max(stats))/2,
                                        xanchor = 'left', yanchor = 'middle',
                                        borderpad = 2,
                                        text = label,
                                        textangle = 0,
                                        font = dict(family = 'Arial', size = 12, color = 'plum'),
                                        showarrow = False
                                        )]
        
                    fig.update_layout(annotations = annotations),
               
                
            return fig
        
        ### Callback for the Map
        @app.callback(Output('map', 'figure'),
                     [Input('barchart', 'clickData'),
                      Input('demodrop', 'value'),
                      Input('basemapdrop', 'value'),
                      Input('rampdrop', 'value'),
                      Input('scaledrop', 'value'),
                      Input('sizedrop', 'value'),
                      Input('metdrop', 'value')
                      ])  
        def makemap (clickdata, demo, basemap, ramp, scale, dotsize, metric):
            
            dff = xlsheet 
            dff['logmetric'] = np.log10(dff['MIR (in a million)'])
            
        #    print(dff.head(10))
            
            if clickdata is None:
                cenlat = dff['Latitude'].mean()
                cenlon = dff['Longitude'].mean()
                zoom = 3
                                  
            else:        
                print(clickdata)
                fac = clickdata['points'][0]['x']
                dfFac = dff.loc[dff['Facility'] == fac]
                cenlat = dfFac['Latitude'].mean()
                cenlon = dfFac['Longitude'].mean()
                zoom = 15
            
            if scale == 'log':
                prefix = '1E '
                color = np.log10(dff[metric])
                
            else:
                prefix = ''
                color = metric
                
            hoverdata = ['Block ID', 'MIR (in a million)', 'Cancer Incidence','Respiratory HI', 'Liver HI', 'Neurological HI', 'Developmental HI',
                 'Reproductive HI', 'Kidney HI', 'Ocular HI', 'Endocrine HI', 'Hematological HI', 'Immunological HI',
                 'Skeletal HI', 'Spleen HI', 'Thyroid HI',  'Latitude', 'Longitude']
                       
            fig = px.scatter_mapbox(dff, lat = 'Latitude', lon = 'Longitude', color = color,
                                    mapbox_style = basemap, color_continuous_scale=ramp, opacity = 1, zoom = zoom,
                                    center = dict(lat = cenlat, lon = cenlon),
                                    hover_name = 'Facility',
                                    hover_data = hoverdata                           
                                    )
            fig.update_traces(marker=dict(size=dotsize))
            fig.update_layout(title = '<b>Facility Map - {}</b>'.format(metric),
                              title_font=dict(size = 22, color = 'black'), uirevision = 'foo',
                              )
            fig.update_coloraxes(colorbar_tickprefix= prefix, colorbar_title = metric)
            return fig
           
         
        @app.callback(Output('table', 'data'),
                      [Input('my-slider', 'value'),
                       Input('radio', 'value')
                      ])        
        def maketable (slidepct, radval):
            if slidepct is None:
                slidepct = 0
            else:
                tabledf = pd.DataFrame(columns = ['Metric', 'Distance (km)', 'Risk Level', 'Total Facility Count', 'Average'] + demogroups)        
                scensComp = maindf.drop_duplicates(subset =['Metric', 'Distance', 'Risk_Level', 'RiskorProx'])
                scensComp.reset_index(inplace = True, drop = True)
                counter = 0
                
                for scen in scensComp.itertuples():
                    tabletemp = pd.DataFrame(columns = ['Metric', 'Distance (km)', 'Risk Level', 'Total Facility Count', 'Average'] + demogroups)
                    if scen.RiskorProx == 'Proximity':
                        comptemp = maindf.loc[(maindf['Metric'] == scen.Metric) & (maindf['Distance'] == scen.Distance) &
                                              (maindf['Risk_Level'] == scen.Risk_Level) & (maindf['RiskorProx'] == 'Proximity')]
                        level = 'Proximity Only'
                    else:
                        comptemp = maindf.loc[(maindf['Metric'] == scen.Metric) & (maindf['Distance'] == scen.Distance) &
                                              (maindf['Risk_Level'] == scen.Risk_Level) & (maindf['RiskorProx'] != 'Proximity')]
                        level = scen.Risk_Level
                    facCount = len(comptemp[comptemp['Total Pop']>0])
                    
                    for i, basis in enumerate(['Nationwide', 'State', 'County']):
                        tabletemp.at[counter, 'Metric'] =  scen.Metric
                        tabletemp.at[counter, 'Distance (km)'] = scen.Distance
                        tabletemp.at[counter, 'Risk Level'] = level
                        tabletemp.at[counter, 'Total Facility Count'] = facCount
                        tabletemp.at[counter, 'Average'] = basis
                        for group in demogroups:
                            avg = compdf.loc[(compdf['Average'] == basis) & (compdf['Distance'] == scen.Distance), group].values[0]
                            if radval == 'num':
                                cellval = len(comptemp[comptemp[group]/100 > (1 + slidepct/100)*avg])
                            else:
                                if facCount == 0:
                                    cellval = '{}%'.format(0)
                                else:
                                    cellval = '{}%'.format(round(len(comptemp[comptemp[group]/100 > (1 + slidepct/100)*avg])/facCount*100))
                            tabletemp.at[counter, group] = cellval
        
                        counter += 1    
                    tabledf = tabledf.append(tabletemp, ignore_index = True)
                    data=tabledf.to_dict('records')
            
            return data


#        @app.callback(
#            Output(component_id='input2', component_property='children'),
#            [Input(component_id='input1', component_property='value')]
#        )
#        def check_status(value):
#            self.shutdown()
#            return 'Shutting down server'
        
        
        @app.callback(
            Output('button-clicks', 'children'),
            [Input('dirbutton', 'n_clicks')])
        def getSecondDir(n_clicks):
            root = tk.Tk()
            root.lift()
            root.withdraw()
            seconddir = None
            if n_clicks is not None:
                seconddir= tk.filedialog.askdirectory()
            root.destroy()
            return seconddir

        app.clientside_callback(
            """
            function() {
            alert(“Client side callback triggered”);
            document.getElementById("dirbutton").focus(); //use this to set the focus on whatever component you want
            //document.getElementById("dirbutton").blur(); //this will remove the focus from a selected component
            return;
            }
            """,
            Output('input2', 'value'), #Callback needs an output, so this is dummy
            [Input('dirbutton', 'n_clicks')] #This triggers the javascript callback
        )            
        
        return app


    def shutdown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        time.sleep(20)
        func()

        
##------------- Code to run the class ----------------------------------------    
#
## Directory to process
#dirtouse = r"C:\Git_HEM4\HEM4\output\PrimCopperActual"
#
## Instansiate
#ejdashapp = EJdash(dirtouse)
#
## If possible, build the app
#try:
#    ejappobj = ejdashapp.buildApp()
#except BaseException as ex:
#    exception = ex
#    fullStackInfo=''.join(traceback.format_exception(
#        etype=type(ex), value=ex, tb=ex.__traceback__))
#    print("Error: ", fullStackInfo)
#
## Display results
#if ejappobj != None:
#    webbrowser.open_new('http://localhost:8050/')
#    ejappobj.run_server(debug= False, port=8050)

