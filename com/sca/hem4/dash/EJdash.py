# -*- coding: utf-8 -*-

import fnmatch
import os
import sys
import pandas as pd
import numpy as np
from tkinter import messagebox

import plotly
import plotly.express as px
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from flask import request
from com.sca.hem4.gui.EJ import EJ
from com.sca.hem4.log.Logger import Logger


class EJdash():

    def __init__(self, dirtouse):
        self.dir = dirtouse
        self.SCname = os.path.split(self.dir)[1]

    def resource_path(self, relative_path):
        # get absolute path to resource
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            cd = os.path.abspath(".")
            base_path = os.path.join(cd, 'com\\sca\\hem4\\dash')
                
        return os.path.join(base_path, relative_path)


    def buildApp(self):

        # Make sure a directory was selected and it contains EJ results
        if self.dir:
            ejdir = os.path.join(self.dir, 'ej')
            if not os.path.isdir(ejdir):
                messagebox.showinfo("Missing ej sub-directory", "The directory chosen does not contain an ej sub-directory. Please ensure that the "+
                                    "Demographic Assessment tool has been run on this directory.")
                return None
        else:
            return None

        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets, assets_folder=self.resource_path('assets'))
        app.title = self.SCname + ' Demographic Assessment'
        
        mapbox_access_token = 'pk.eyJ1IjoiYnJ1enp5IiwiYSI6ImNrOTE5YmwzdDBhMXYzbW8yMjY4aWJ3eHQifQ.5tNjnlK2Y8b-U1kvfPP8FA'
        px.set_mapbox_access_token(mapbox_access_token)
        #pd.set_option("display.max_columns", 50)
        #pd.options.display.max_colwidth = 50
        
        ### create dictionary of metrics for display purposes
        toshis = EJ('foo').toshis
        display_mets = {k:v + ' HI' for (k,v) in toshis.items()}
        display_mets['Cancer'] = 'Cancer Risk'
        
        ### Get markdown text
        bar_instr = open('instructions/ejdash_bar.txt', 'r').read()
        map_instr = open('instructions/ejdash_map.txt', 'r').read()
        table_instr = open('instructions/ejdash_table.txt', 'r').read()
       
                
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


        # Record the number of people age >= 25 for each facility for proximity and risk/HI level.
        # Use dictionary where key is facility + metric + distance + level + risk/prox
        age25pop = {}
        list_subfolders_nameonly = [f.name for f in os.scandir(ejdir) if f.is_dir()]
        for subfolder in list_subfolders_nameonly:
            facilityID = subfolder
            facfolder = os.path.join(ejdir, subfolder)
            facfiles = os.listdir(facfolder)
            demofiles = fnmatch.filter(facfiles, '*_demo_*')
            for dfile in demofiles:
               # Parse facility filename to get parameters 
               part1 = dfile.split('_km_',1)[0]
               part2 = dfile.split('_km_',1)[1]
               distance = part1.split('_')[-1]
               level = int(part2.split('_')[0])
               metric = part2.split('_')[2].lower()
               dfile_path = os.path.join(ejdir, subfolder, dfile)
               excel = pd.ExcelFile(dfile_path)
               sheetname = fnmatch.filter(excel.sheet_names, 'Table*3*C')
               dfile_df = pd.read_excel(dfile_path, sheet_name=sheetname[0], 
                                        skiprows=5, nrows = 12, header=None,
                                        names=['range','emptycol','totpop','age25pop','noHS'])
               
               # Define index based on the metric and risk ranges. Key is risk level and value is index number
               r_index = {}
               if metric == "cancer":
                   r_index[0]=0
                   r_index[1]=1
                   r_index[5]=2
                   r_index[10]=3
                   r_index[20]=4
                   r_index[30]=5
                   r_index[40]=6
                   r_index[50]=7
                   r_index[100]=8
                   r_index[200]=9
                   r_index[300]=10
               else:
                   r_index[0]=0
                   r_index[1]=1
                   r_index[2]=2
                   r_index[3]=3
                   r_index[4]=4
                   r_index[5]=5
                   r_index[6]=6
                   r_index[7]=7
                   r_index[8]=8
                   r_index[9]=9
                   r_index[10]=10
               
               # Count of age 25 and up based on the risk/HI level
               riskage25 = dfile_df.iloc[r_index[level]:-1,3].sum()
               age25pop[facilityID+'_'+metric+'_'+distance+'_'+str(level)+'_risk'] = riskage25
                   
               # Count of age 25 and up based on proximity
               proxage25 = dfile_df.iloc[11,3]
               age25pop[facilityID+'_'+metric+'_'+distance+'_'+str(level)+'_prox'] = proxage25
        
        ##### Get EJ summary files
        pattern_list = ["*Summary*"]
        files = os.listdir(ejdir)
        for pattern in pattern_list:
            file_list = fnmatch.filter(files, pattern)
         
        # Make sure there are unique rungroups in this folder
        rungroups = [i.split('_EJ-Summary_',1)[0] for i in file_list]
        rungroups_unique = set(rungroups)
        if len(rungroups_unique) > 1:
            emessage = ("The rungroup names on the files in this folder are " +
                        "not unique. Please correct this before running this application. The following rungroup names were found: \n" +
                        ",".join(list(rungroups_unique)))
            messagebox.showinfo('Rungroup names not unique', emessage)
            Logger.logMessage(emessage)
            raise Exception(emessage)
                        
            
        rungroup = file_list[0].split('_EJ-Summary_')[0]
        demogroups = ['People of Color', 'African American','Native American', 'Other and Multiracial', 'Hispanic or Latino',
                      'Age 0-17', 'Age 18-64', 'Age >=65','Below the Poverty Level', 
                      'Below Two Times the Poverty Level', 'Over 25 Without a High School Diploma',
                      'Linguistically Isolated']
        
        ### Go through the files (and sheets within files) to get all the scenarios run in the Demographic Assessment module
        scenarios = pd.DataFrame(columns = ['Metric', 'Distance', 'Risk_Level', 'Filename'])
        scen_ind = 0
                
        for file in file_list:
                tail = file.split('_EJ-Summary_')[1]
                extension = tail.split('_')[-1]
                metric = tail.split('_')[2]
                distance = tail.split('_')[0]
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
        compnames = ['Average', 'Total Pop', 'People of Color', 'African American','Native American',
                     'Other and Multiracial', 'Hispanic or Latino','Age 0-17', 'Age 18-64', 'Age >=65',
                     'Below the Poverty Level', 'Below Two Times the Poverty Level',
                     'Over 25 Without a High School Diploma','Linguistically Isolated']
        compdf = pd.DataFrame()
        
        for scen in scenarios.itertuples():
            temp = pd.read_excel(scen.Filename, skiprows = [0,1], usecols = [0, 2,3,4,5,6,7,8,9,10,11,12,13,14],
                                 names = compnames
                                 )
            compdata = temp.loc[temp['Average'].isin(['Nationwide', 'State', 'County'])]
            compdata['Distance'] = scen.Distance
            compdf = compdf.append(compdata)
        
        compdf.drop_duplicates(inplace = True)
        
        ### Create a dataframe of the facility data  
        mainnames = ['Facility', 'RiskorProx', 'Total Pop', 'People of Color', 'African American','Native American',
                     'Other and Multiracial', 'Hispanic or Latino','Age 0-17', 'Age 18-64', 'Age >=65',
                     'Below the Poverty Level', 'Below Two Times the Poverty Level',
                     'Over 25 Without a High School Diploma','Linguistically Isolated']        
        maindf = pd.DataFrame()
        noprox = scenarios[~scenarios['Risk_Level'].isin(['Proximity Only'])]
        
        for file in file_list:
            fname = os.path.join(ejdir, file)
            tail = file.split('_EJ-Summary_')[1]
            xl = pd.ExcelFile(fname)
            sheets = xl.sheet_names
            for sheet in sheets:
        
                # Read Excel sheet as dtype string and then convert columns 2 onward to float.
                # This ensures the facility ID is a string.
                temp = xl.parse(skiprows = [0,1,3,4,5,6,7,8,9], names = mainnames, sheet_name=sheet, dtype=str)
                temp[temp.columns[2:]] = temp[temp.columns[2:]].astype(float)
                temp.insert(0, 'Metric', tail.split('_')[2])
                temp.insert(1, 'Distance', tail.split('_')[0])
                temp.insert(2, 'Risk_Level', sheet)
                
                ## Adding cols for demog group pop; and facility names in rows where absent
                ## Note: over 25 without a HS diploma uses count of people over age 25, not total pop
                for col in demogroups:
                    newcol = col + ' Pop'
                    if col != 'Over 25 Without a High School Diploma':
                        temp[newcol] = (temp[col] * temp['Total Pop'])
                    else:
                        temp[newcol] = 0
                        
                for i, row in temp.iterrows():
#                    if pd.isna(row[3]):
                    if row[3] == 'nan':
                        # Store the facility id in the DF
                        temp.iat[i,3] = temp.iat[i-1,3]
                    
                    # Fill-in over age 25 pop
                    # key = facility id + metric + distance + risk/HI level + prox/risk
                    if sheet[0] == 'R':
                        rlevel = sheet[sheet.find("=")+2:sheet.find("-")]
                    else:
                        rlevel = sheet[sheet.find(">")+2:]
                        
                    if row['RiskorProx'] == 'Proximity':
                        age25pop_key = temp.iloc[i,3] + '_' + temp.iloc[i,0].lower() + '_' + temp.iloc[i,1] + '_' + rlevel + '_prox'
                    else:
                        age25pop_key = temp.iloc[i,3] + '_' + temp.iloc[i,0].lower() + '_' + temp.iloc[i,1] + '_' + rlevel + '_risk'                        
                    count_age25up = age25pop[age25pop_key]
                    temp.loc[i, 'Over 25 Without a High School Diploma Pop'] = \
                                temp.loc[i, 'Over 25 Without a High School Diploma'] * count_age25up

                
                # Convert the decimal fractions to percents for the demo groups        
                for col in demogroups:
                    temp[col] = 100 * temp[col]
                
                maindf = maindf.append(temp, ignore_index = True)
         
        ##### The app layout 
        app.layout = html.Div([
            
                html.Div([
                        html.H1("Demographic Assessment for HEM4 Run Group " + rungroup, style={'text-align':'center', 'font-weight': 'bold'}),
                        ], className = 'row'),
            
                dcc.Tabs([
                        dcc.Tab(label="Bar Graph", children=[
        
                            
                                ###########  Start Chart Dropdowns  ##########
                                
                                html.Div([
                                    
                                    html.Div([html.H6("Risk Metric"),
                                             dcc.Dropdown(id='riskdrop',
                                                          options=[{"label": display_mets[i], "value": i} for i in metrics],
#                                                          options=[{"label": v, "value": k} for k,v in display_mets],
                                                          multi=False,
                                                          clearable=False,
                                                          value = scenarios.loc[0, 'Metric'],
                                                          placeholder="Select a Metric",
                                                          ),
                                            ], className = 'two columns'),
                                             
                                    html.Div([html.H6("Distance (km)"),
                                              dcc.Dropdown(id='distdrop',             
                                                          multi=False,
                                                          clearable=False,
                                                          value = scenarios.loc[0, 'Distance'],
                                                          placeholder="Select a Distance (km)",
                                                          ),
                                            ], className = 'two columns'),
                                    
                                    html.Div([html.H6("Risk/HI Level"),
                                              dcc.Dropdown(id='leveldrop',
                                                          multi=False,
                                                          clearable=False,
                                                          value = scenarios.loc[0, 'Risk_Level'],
                                                          placeholder="Select a Risk or HI Level",
                                                          ),
                                            ], className = 'two columns'),
                                                           
                                    html.Div([html.H6("Demographic Group"),
                                              dcc.Dropdown(id='demodrop',
                                                           
                                                          options=[{"label": i, "value": i} for i in demogroups],
                                                          multi=False,
                                                          clearable=False,
                                                          value = 'People of Color',
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
                                                  },
                                                  
                                        ),
                                        html.Hr()
                                        ], className='twelve columns'),
            
                        ]),
                
                        dcc.Tab(label="Map of Facilities", children=[
                                
                                
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
                                                               {"label": 'Blue to Yellow', "value": px.colors.sequential.Cividis},
                                                               {"label": 'Purple to Yellow', "value": px.colors.sequential.Viridis},
                                                               {"label": 'Blue Scale', "value": px.colors.sequential.Blues},
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
                                                       
                        dcc.Tab(label="Summary Table", children=[
                                                     
                                       
                                html.Div(id='callbackTable'),
                                
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
                                dcc.Tabs([
                                        dcc.Tab(label='About the Bar Graph',children=[
                                                dcc.Markdown(bar_instr),
                                        ]),
                                        dcc.Tab(label='About the Map',children=[
                                                dcc.Markdown(map_instr),
                                        ]),
                                        dcc.Tab(label='About the Summary Table',children=[
                                                dcc.Markdown(table_instr),
                                        ]),
                                ]),
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
                    dff = dff.drop_duplicates(subset=['Distance','Facility'], keep='first')
                else:
                    dff = maindf.loc[(maindf['Metric'] == risk) & (maindf['Distance'] == distance) & (maindf['Risk_Level'] == level) &
                                     (maindf['RiskorProx'] != 'Proximity')]
                    dff = dff.drop_duplicates(subset=['Distance','Facility','Metric','Risk_Level'], keep='first')
                
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
                    title = '<b>Demographics for ' + display_mets[risk] + ' for Radius ' + distance + ' km (Proximity Only)</b>'
                    
                else:
                    title = '<b>Demographics for ' + display_mets[risk] + ' for Radius ' + distance + ' km (' + level +')</b>'
                    
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
                
                hoverdata = {group: ':.1f',
                             group +' Pop': ':0f'}
                                
                fig = px.bar(dff, x='Facility', y=yaxis, height=800, width=1500, text = text,opacity=.7, hover_data=hoverdata)
                fig.update_yaxes(type = type, title_text=ytitle, title_font=dict(size = 16, color = 'black'), automargin=True)
                fig.update_xaxes(title_text='<b>Facility</b>', title_font=dict(size = 16, color = 'black'), automargin=True, tickangle=40,
                                 type = 'category', range = (-.5, min(numFacs,50)))
                fig.update_layout(title = title, title_font=dict(size = 22, color = 'black'),
                                  clickmode="event+select", hovermode = 'closest',
                                  margin=dict(r=100))
                fig.update_traces(texttemplate=texttemplate)
                
                stats = [natwide,statwide,countwide]
                label = "<b>Nation: {}%<br> State: {}%<br> County: {}%</b>".format(natwide, statwide, countwide)
                   
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
                
#            hoverdata = ['Block ID', 'MIR (in a million)', 'Cancer Incidence','Respiratory HI', 'Liver HI', 'Neurological HI', 'Developmental HI',
#                 'Reproductive HI', 'Kidney HI', 'Ocular HI', 'Endocrine HI', 'Hematological HI', 'Immunological HI',
#                 'Skeletal HI', 'Spleen HI', 'Thyroid HI',  'Latitude', 'Longitude']
            
            hoverdata={
                    'MIR (in a million)':':.1e',
                    'Respiratory HI':':.1e',
                    'Liver HI':':.1e',
                    'Neurological HI':':.1e',
                    'Developmental HI':':.1e',
                    'Reproductive HI':':.1e',
                    'Kidney HI':':.1e',
                    'Ocular HI':':.1e',
                    'Endocrine HI':':.1e',
                    'Hematological HI':':.1e',
                    'Immunological HI':':.1e',
                    'Skeletal HI':':.1e',
                    'Spleen HI':':.1e',
                    'Thyroid HI':':.1e',
                    'Latitude':':.7f',
                    'Longitude':':.7f',
                    }
            
#            if scale == 'log':
#                    hoverdata['color'] = False
                       
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
           
         
        @app.callback(Output('callbackTable', 'children'),
                      [Input('my-slider', 'value'),
                       Input('radio', 'value')
                      ])        
        def maketable (slidepct, radval):
                       
            if None in (slidepct, radval):
                pass
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
                        tabletemp.at[counter, 'Metric'] =  display_mets[scen.Metric]
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
                
                if radval == 'num':
                    prefix = 'Number'
                else:
                    prefix = 'Percent'
                    
                if slidepct == 0:
                    suffix = ''
                else:
                    suffix = 'by More Than {}%'.format(slidepct)
                    
                grphead = '{} of Facilities Exceeding the Geographic Average {}'.format(prefix, suffix)
                    
            #        if radval == 'num':
            #            grphead = 'Number of Facilities Exceeding the Geographic Average'
            #        else:
            #            grphead = 'Percent of Facilities Exceeding the Geographic Average'
                    
                table = dash_table.DataTable(
                                             
                        columns=[
                                {"name": ['Scenario', 'Metric'], "id": 'Metric', 'presentation': 'dropdown'},
                                {"name": ['Scenario', 'Distance (km)'], "id": 'Distance (km)', 'presentation': 'dropdown'},
                                {"name": ['Scenario', 'Risk Level'], "id": 'Risk Level', 'presentation': 'dropdown'},
                                {"name": ['Scenario', 'Total Facility Count'], "id": 'Total Facility Count'},
                                {"name": ['', 'Average'], "id": 'Average', 'presentation': 'dropdown'},
                                {"name": [grphead, 'People of Color'], "id": 'People of Color'},
                                {"name": [grphead, 'African American'], "id": 'African American'},
                                {"name": [grphead, 'Native American'], "id": 'Native American'},
                                {"name": [grphead, 'Other and Multiracial'], "id": 'Other and Multiracial'},
                                {"name": [grphead, 'Hispanic or Latino'], "id": 'Hispanic or Latino'},
                                {"name": [grphead, 'Age 0-17'], "id": 'Age 0-17'},
                                {"name": [grphead, 'Age 18-64'], "id": 'Age 18-64'},
                                {"name": [grphead, 'Age >=65'], "id": 'Age >=65'},
                                {"name": [grphead, 'Below the Poverty Level'], "id": 'Below the Poverty Level'},
                                {"name": [grphead, 'Below Two Times the Poverty Level'], "id": 'Below Two Times the Poverty Level'},
                                {"name": [grphead, 'Over 25 Without a High School Diploma',], "id": 'Over 25 Without a High School Diploma',},
                                {"name": [grphead, 'Linguistically Isolated'], "id": 'Linguistically Isolated'}
                                
                        ],
                        
                        dropdown={
                                'Metric': {                               
                                    'options': [
                                        {'label': i, 'value': i}
                                        for i in tabledf['Metric'].unique()
                                    ],
                                    'clearable':True
                                },
                                'Distance (km)': {
                                    'options': [
                                        {'label': i, 'value': i}
                                        for i in tabledf['Distance (km)'].unique()
                                    ],
                                    'clearable':True
                                },
                                'Risk Level': { 
                                    'options': [
                                        {'label': i, 'value': i}
                                        for i in tabledf['Risk Level'].unique()
                                    ],
                                    'clearable':True
                                },
                                'Average': {
                                    'options': [
                                        {'label': i, 'value': i}
                                        for i in tabledf['Average'].unique()
                                    ],
                                    'clearable':True
                                }
                        },
                                        
                        merge_duplicate_headers=True,
                        data=tabledf.to_dict('records'),
                        page_action='none',     # render all of the data at once
                        filter_action = 'native',
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
    
            return table
        
        return app


        @app.server.route('/shutdown', methods=['GET'])
        def shutdown():
            print("Shutting down server")
            self.shutdown_server()
            return 'Server shutting down...'
        
        
#        @app.callback(
#            Output('button-clicks', 'children'),
#            [Input('dirbutton', 'n_clicks')])
#        def getSecondDir(n_clicks):
#            root = tk.Tk()
#            root.lift()
#            root.withdraw()
#            seconddir = None
#            if n_clicks is not None:
#                seconddir= tk.filedialog.askdirectory()
#            root.destroy()
#            return seconddir
#
#        app.clientside_callback(
#            """
#            function() {
#            alert(“Client side callback triggered”);
#            document.getElementById("dirbutton").focus(); //use this to set the focus on whatever component you want
#            //document.getElementById("dirbutton").blur(); //this will remove the focus from a selected component
#            return;
#            }
#            """,
#            Output('input2', 'value'), #Callback needs an output, so this is dummy
#            [Input('dirbutton', 'n_clicks')] #This triggers the javascript callback
#        )            
        
        return app

             
                            

    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
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

