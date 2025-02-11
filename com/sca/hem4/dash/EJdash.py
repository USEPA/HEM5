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
from dash import dash_table, dcc, html, no_update
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

        # Make sure a directory was selected and it contains demographic results
        if self.dir:
            ejdir = os.path.join(self.dir, 'pop')
            if not os.path.isdir(ejdir):
                messagebox.showinfo("Missing pop sub-directory", "The directory chosen does not contain a pop sub-directory. Please ensure that the "+
                                    "Demographic Assessment tool has been run on this directory.")
                return None
        else:
            return None

        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets, assets_folder=self.resource_path('assets'))
        app.title = self.SCname + ' Demographic Assessment'
                
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
        rungroups = [i.split('_Pop-Summary_',1)[0] for i in file_list]
        rungroups_unique = set(rungroups)
        if len(rungroups_unique) > 1:
            emessage = ("The rungroup names on the files in this folder are " +
                        "not unique. Please correct this before running this application. The following rungroup names were found: \n" +
                        ",".join(list(rungroups_unique)))
            messagebox.showinfo('Rungroup names not unique', emessage)
            Logger.logMessage(emessage)
            raise Exception(emessage)
                        
            
        rungroup = file_list[0].split('_Pop-Summary_')[0]
        demogroups = ['People of Color', 'Black','American Indian or Alaska Native', 'Asian',
                      'Other and Multiracial', 'Hispanic or Latino',
                      'Age 0-17', 'Age 18-64', 'Age >=65','Below Poverty Level', 
                      'Below Twice Poverty Level', 'No High School Diploma',
                      'Limited English Speaking Households', 'People with Disabilities']
        
        ### Go through the files (and sheets within files) to get all the scenarios run in the Demographic Assessment module
        scenarios = pd.DataFrame(columns = ['Metric', 'Distance', 'Risk_Level', 'Filename'])
        scen_ind = 0
                
        for file in file_list:
                tail = file.split('_Pop-Summary_')[1]
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
                    fname = os.path.join(ejdir, rungroup + '_Pop-Summary_' + distance + '_km_' + metric + '_' + extension)
                    scenarios.loc[scen_ind, 'Filename'] = fname
                    scen_ind +=1
        
        
        scenarios['scen_label'] = scenarios['Metric'].map(display_mets) + ' -- ' + scenarios['Risk_Level'] + ' -- Out to ' + scenarios['Distance'] + ' km'
        scenarios_sort = scenarios.sort_values(by='scen_label').copy()
        
        metrics = scenarios['Metric'].unique()
                
        ### Create a dataframe of the national, state, and county averages
        compnames = ['Average', 'Total Pop', 'People of Color', 'Black','American Indian or Alaska Native',
                     'Asian', 'Other and Multiracial', 'Hispanic or Latino','Age 0-17', 'Age 18-64', 'Age >=65',
                     'Below Poverty Level', 'Below Twice Poverty Level',
                     'No High School Diploma','Limited English Speaking Households',
                     'People with Disabilities']
        compdf = pd.DataFrame()
        
        for scen in scenarios.itertuples():
            temp = pd.read_excel(scen.Filename, skiprows = [0,1], usecols = [0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
                                 names = compnames, header=None
                                 )
            # Remove blank rows and footnotes
            temp = temp[temp['Average'].notna() & temp['Total Pop'].notna()]
            
            # compdata = temp.loc[temp['Average'].isin(['Nationwide', 'State', 'County'])]
            compdata = temp.loc[temp['Average'].str.contains("Nationwide|State|County", case=True)].copy()
            compdata['Distance'] = scen.Distance
            compdf = pd.concat([compdf, compdata])
        
        compdf.drop_duplicates(inplace = True)
        
        ### Create a dataframe of the facility data  
        mainnames = ['Facility', 'RiskorProx', 'Total Pop', 'People of Color', 'Black',
                     'American Indian or Alaska Native', 'Asian',
                     'Other and Multiracial', 'Hispanic or Latino','Age 0-17', 'Age 18-64', 'Age >=65',
                     'Below Poverty Level', 'Below Twice Poverty Level',
                     'No High School Diploma','Limited English Speaking Households',
                     'People with Disabilities']        
        maindf = pd.DataFrame()
        noprox = scenarios[~scenarios['Risk_Level'].isin(['Proximity Only'])]
        
        for file in file_list:
            fname = os.path.join(ejdir, file)
            tail = file.split('_Pop-Summary_')[1]
            xl = pd.ExcelFile(fname)
            sheets = xl.sheet_names
            for sheet in sheets:
        
                # Read Excel sheet as dtype string and then convert columns 2 onward to float.
                # This ensures the facility ID is a string.
                temp = xl.parse(skiprows = [0,1,3,4,5,6,7,8], names = mainnames, sheet_name=sheet, dtype=str)
                temp[temp.columns[2:]] = temp[temp.columns[2:]].astype(float)
                temp.insert(0, 'Metric', tail.split('_')[2])
                temp.insert(1, 'Distance', tail.split('_')[0])
                temp.insert(2, 'Risk_Level', sheet)
                
                # Remove blank rows or rows with footnotes
                temp = temp[temp['RiskorProx'].notna()]

                
                ## Adding cols for demog group pop; and facility names in rows where absent
                ## Note: over 25 without a HS diploma uses count of people over age 25, not total pop
                for col in demogroups:
                    newcol = col + ' Pop'
                    if col != 'No High School Diploma':
                        temp[newcol] = (temp[col] * temp['Total Pop'])
                    else:
                        temp[newcol] = 0

                                
                for i, row in temp.iterrows():
                    if pd.isna(row[3]) == True:
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
                    temp.loc[i, 'No High School Diploma Pop'] = \
                                temp.loc[i, 'No High School Diploma'] * count_age25up
                
                # Convert the decimal fractions to percents for the demo groups        
                for col in demogroups:
                    temp[col] = 100 * temp[col]
                                    
                maindf = pd.concat([maindf, temp], ignore_index = True)
                
                
        ##### The app layout 
        app.layout = html.Div([
            
                # dcc.Store(id='metricdropstore'),    
                # dcc.Store(id='distdropstore'),
                # dcc.Store(id='leveldropstore'),
            
                html.Div([
                        html.H2("Demographic Assessment for HEM Run Group " + rungroup, style={'text-align':'center', 'font-weight': 'bold'}),
                        ], className = 'row'),
            
                dcc.Tabs([
                        dcc.Tab(label="Bar Graph", children=[
        
                            
                                ###########  Start Chart Dropdowns  ##########
                                
                                html.Div([
                                    
                                    html.Div([html.H6("Scenario"),
                                             dcc.Dropdown(id='scendrop',
                                                          options=[{"label": i, "value": i} for i in scenarios_sort['scen_label']],
#                                                          options=[{"label": v, "value": k} for k,v in display_mets],
                                                          multi=False,
                                                          clearable=False,
                                                          value = scenarios_sort.at[0,'scen_label'],
                                                          placeholder="Select a Scenario",
                                                          ),
                                            ], className = 'four columns'),
                                    

                                                           
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
                                        # dcc.Tab(label='About the Map',children=[
                                        #         dcc.Markdown(map_instr),
                                        # ]),
                                        dcc.Tab(label='About the Summary Table',children=[
                                                dcc.Markdown(table_instr),
                                        ]),
                                ]),
                        ]),
                ]),
        
                              
        ])
 
           
        
        ### Callback for the Bar Chart
        @app.callback(Output('barchart', 'figure'),
                     [Input('scendrop', 'value'),
                    # Input('riskdrop', 'value'),
                    #   Input('distdrop', 'value'),
                    #   Input('leveldrop', 'value'),
                      Input('demodrop', 'value'),
                      Input('barhtdrop', 'value'),
                      Input('sortdrop', 'value')
                     ])
        def makebar (scen, group,barht, sort):
            if None in [scen, group]:
                return no_update
            else:
                scenrow = scenarios_sort.loc[scenarios_sort['scen_label'] == scen]
                risk = scenrow.iat[0,0]
                distance = scenrow.iat[0,1]
                level = scenrow.iat[0,2]
                
                if level == 'Proximity Only':
                    dff = maindf.loc[(maindf['Metric'] == risk) & (maindf['Distance'] == distance) & (maindf['RiskorProx'] == 'Proximity')].copy()
                    dff = dff.drop_duplicates(subset=['Distance','Facility'], keep='first')
                else:
                    dff = maindf.loc[(maindf['Metric'] == risk) & (maindf['Distance'] == distance) & (maindf['Risk_Level'] == level) &
                                     (maindf['RiskorProx'] != 'Proximity')].copy()
                    dff = dff.drop_duplicates(subset=['Distance','Facility','Metric','Risk_Level'], keep='first')
                
                if sort == 'Pct':
                    sorter = group
                else:
                    sorter = group + ' Pop'
                
                dff = dff.loc[(dff[group] > 0) & (dff[group + ' Pop'] >= 1)].sort_values(by=[sorter], ascending = False).copy()
                
                dff = dff.round(decimals = 1)
                
                ### Get max value for the demog group
                groupmax = dff[group].max()
                           
                ### Get the geographic averages for the given distance and demographic group
                natwide = compdf.loc[(compdf['Average'].str.contains('Nationwide', case=True)) & (compdf['Distance'] == distance), group]
                statwide = compdf.loc[(compdf['Average'].str.contains('State', case=True)) & (compdf['Distance'] == distance), group]
                countwide = compdf.loc[(compdf['Average'].str.contains('County', case=True)) & (compdf['Distance'] == distance), group]
                natwide = round(natwide[0]*100,1)
                statwide = round(statwide[1]*100,1)
                countwide = round(countwide[2]*100,1)
                stats = [natwide,statwide,countwide]
                
                ### Get overall max value
                overall_max = max(stats + [groupmax])
                ybar_max = min(overall_max + 10, 100)
                
                
                ### Set chart title based on user choice of proximity or risk        
                if level == 'Proximity Only':
                    title = '<b>Demographics for Radius ' + distance + ' km (Proximity Only)</b>'
                    
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
                    brange = None
                    
                else:
                    yaxis = group
                    text = group +' Pop'
                    texttemplate = '%{text:,.0f}'
                    ytitle = '<b>' + group + ' (%)</b>'
                    type = 'linear'
                    brange = [0,ybar_max]
                
                hoverdata = {group: ':.1f%', group + ' Pop': ':,0f'}
                
                fig = px.bar(dff, x='Facility', y=yaxis, height=800, width=1500, text = text,opacity=.7, hover_data=hoverdata)
                              
                fig.update_yaxes(type = type, title_text=ytitle, title_font=dict(size = 16, color = 'black'), automargin=True, range=brange)
                if numFacs > 0:
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
                                              (maindf['Risk_Level'] == scen.Risk_Level) & (maindf['RiskorProx'] == 'Proximity')].copy()
                        level = 'Proximity Only'
                    else:
                        comptemp = maindf.loc[(maindf['Metric'] == scen.Metric) & (maindf['Distance'] == scen.Distance) &
                                              (maindf['Risk_Level'] == scen.Risk_Level) & (maindf['RiskorProx'] != 'Proximity')].copy()
                        level = scen.Risk_Level
                    facCount = len(comptemp[comptemp['Total Pop']>0])
                    
                    for i, basis in enumerate(['Nationwide', 'State', 'County']):
                        tabletemp.at[counter, 'Metric'] =  display_mets[scen.Metric]
                        tabletemp.at[counter, 'Distance (km)'] = scen.Distance
                        tabletemp.at[counter, 'Risk Level'] = level
                        tabletemp.at[counter, 'Total Facility Count'] = facCount
                        tabletemp.at[counter, 'Average'] = basis
                        for group in demogroups:
                            avg = compdf.loc[(compdf['Average'].str.contains(basis, case=True)) & (compdf['Distance'] == scen.Distance), group].values[0]
                            if radval == 'num':
                                cellval = len(comptemp[comptemp[group]/100 > (1 + slidepct/100)*avg])
                            else:
                                if facCount == 0:
                                    cellval = '{}%'.format(0)
                                else:
                                    cellval = '{}%'.format(round(len(comptemp[comptemp[group]/100 > (1 + slidepct/100)*avg])/facCount*100))
                            tabletemp.at[counter, group] = cellval
            
                        counter += 1    
                    tabledf = pd.concat([tabledf, tabletemp], ignore_index = True)
                
                if radval == 'num':
                    prefix = 'Number'
                else:
                    prefix = 'Percent'
                    
                if slidepct == 0:
                    suffix = ''
                else:
                    suffix = 'by More Than {}%'.format(slidepct)
                    
                grphead = '{} of Facilities Exceeding the Geographic Average {}'.format(prefix, suffix)
                    
                    
                table = dash_table.DataTable(
                                             
                        columns=[
                                {"name": ['Scenario', 'Metric'], "id": 'Metric', 'presentation': 'dropdown'},
                                {"name": ['Scenario', 'Distance (km)'], "id": 'Distance (km)', 'presentation': 'dropdown'},
                                {"name": ['Scenario', 'Risk Level'], "id": 'Risk Level', 'presentation': 'dropdown'},
                                {"name": ['Scenario', 'Total Facility Count'], "id": 'Total Facility Count'},
                                {"name": ['', 'Average'], "id": 'Average', 'presentation': 'dropdown'},
                                {"name": [grphead, 'People of Color'], "id": 'People of Color'},
                                {"name": [grphead, 'Black'], "id": 'Black'},
                                {"name": [grphead, 'American Indian or Alaska Native'], "id": 'American Indian or Alaska Native'},
                                {"name": [grphead, 'Asian'], "id": 'Asian'},
                                {"name": [grphead, 'Other and Multiracial'], "id": 'Other and Multiracial'},
                                {"name": [grphead, 'Hispanic or Latino'], "id": 'Hispanic or Latino'},
                                {"name": [grphead, 'Age 0-17'], "id": 'Age 0-17'},
                                {"name": [grphead, 'Age 18-64'], "id": 'Age 18-64'},
                                {"name": [grphead, 'Age ≥65'], "id": 'Age >=65'},
                                {"name": [grphead, 'Below Poverty Level'], "id": 'Below Poverty Level'},
                                {"name": [grphead, 'Below Twice Poverty Level'], "id": 'Below Twice Poverty Level'},
                                {"name": [grphead, 'No High School Diploma',], "id": 'No High School Diploma',},
                                {"name": [grphead, 'Limited English Speaking Households'], "id": 'Limited English Speaking Households'},
                                {"name": [grphead, 'People with Disabilities'], "id": 'People with Disabilities'}
                                
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
                                'fontSize': 16,
                                'border': '1px solid black',
                                'textAlign': 'center',
                                'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                            },
                             
                        style_cell={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'font-family': 'verdana',
                                'fontSize':15,
                                'minWidth': '10px', 'width': '110px', 'maxWidth': '200px'},
                        style_cell_conditional=[
                                {'if': {'row_index': [3,4,5,9,10,11,15,16,17,21,22,23,27,28,29,33,34,35,39,40,41]},
                                 'backgroundColor': 'LightGrey'
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
        
               
        return app

             
                            

    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
                                                       
                                   

        

