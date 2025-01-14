# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 07:07:56 2020

@author: MMORRIS
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
import plotly.express as px
import plotly
import os
from tkinter import messagebox

from flask import request
from concurrent.futures import ThreadPoolExecutor
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


class HEMdash():
    
    def __init__(self, dirtouse):
        self.dir = dirtouse
        self.SCname = self.dir.split('/')[-1]

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
        
        # Make sure a directory was selected and it is a run group directory

        if self.dir:
            facrisk_file = self.SCname + "_facility_max_risk_and_hi.xlsx"
            candriver_file = self.SCname + "_cancer_drivers.xlsx"
            hidriver_file = self.SCname + "_hazard_index_drivers.xlsx"
            incdriver_file = self.SCname + "_incidence_drivers.xlsx"
            srctype_file = self.SCname + "_source_type_risk.xlsx"
            histrisk_file = self.SCname + "_histogram_risk.xlsx"
            histhi_file = self.SCname + "_hi_histogram.xlsx"
            filelist = [facrisk_file, candriver_file, hidriver_file, incdriver_file, srctype_file,
                        histrisk_file, histhi_file]
            while True:
                chklist = []
            
                for file in filelist:
                    fullname = os.path.join(self.dir, file)
                    chklist.append(os.path.isfile(fullname))
                
                if not all(chklist):
                    missingfile_list = [i for (i, v) in zip(filelist, chklist) if not v]
                    missingfile_msg = '\n'.join(missingfile_list)
                    messagebox.showinfo("Invalid directory", "Please select a directory containing the results of a model run and summary reports for cancer risk drivers, "+
                                        "max risks, max TOSHI drivers, pollutant incidence drivers, source type incidence drivers, and cancer histograms. This directory is missing: \n" +
                                        missingfile_msg)
                    return None
                else:
                    break
        else:
            return None
                    

        # Directory is correct. Continue...            
            
        ## Rather than using the external css, could use local "assets" dir that has the css file
        # external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        dbc_stylesheets = [dbc.themes.MORPH]
        
        # External scripts
        chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js"  # js lib used for colors
                
        ct_esri, ct_dark, ct_light, ct_openstreet, ct_places, ct_roads = get_basemaps() # get basemaps and other layers                
                
        app = dash.Dash(__name__, external_stylesheets=dbc_stylesheets, 
                        external_scripts=[chroma], assets_folder=self.resource_path('assets'))
        app.title = 'HEM Summary Results: ' + self.SCname
                
        # Create dataframe of max risks
        fname = self.SCname + "_facility_max_risk_and_hi.xlsx"
        max_rsk_hi = os.path.join(self.dir, fname)
        cols2use = ('A,B,D,E,F,G,H,M,N,Q,R,W,X,AA,AB,AE,AF,AI,AJ,AM,AN,AQ,AR,AU,AV,AY,AZ,BC,BD,BG,BH,BK,BL,BO,BQ,BR,BS,BT,BU,BV')
        dataTypes1 = {'Facil_id':str, 'mx_can_rsk':float, 'can_rcpt_type':str,
               'can_latitude':float, 'can_longitude':float, 'can_blk':str, 'respiratory_hi':float,
               'resp_blk':str, 'liver_hi':float, 'liver_blk':str, 'neurological_hi':float, 'neuro_blk':str,
               'developmental_hi':float, 'devel_blk':str, 'reproductive_hi':float, 'repro_blk':str,
               'kidney_hi':float, 'kidney_blk':str, 'ocular_hi':float, 'ocular_blk':str, 'endocrine_hi':float,
               'endo_blk':str, 'hematological_hi':float, 'hema_blk':str, 'immunological_hi':float,
               'immun_blk':str, 'skeletal_hi':float, 'skel_blk':str, 'spleen_hi':float, 'spleen_blk':str,
               'thyroid_hi':float, 'thyroid_blk':str, 'whole_body_hi':float, 'whole_blk':str, 'incidence':float,
               'metname':str, 'km_to_metstation':int, 'fac_center_latitude':float, 'fac_center_longitude':float,
               'rural_urban':str}
        df_max_can = pd.read_excel(max_rsk_hi, dtype=dataTypes1, usecols = cols2use)
        df_max_can['mx_can_rsk'] = df_max_can['mx_can_rsk'].apply(lambda x: x*1000000)
        df_max_can.columns = ['Facility', 'MIR (in a million)', 'MIR Receptor Type',
               'MIR Lat', 'MIR Lon', 'MIR Block', 'Respiratory HI',
               'Resp Block', 'Liver HI', 'Liver Block', 'Neurological HI', 'Neuro Block',
               'Developmental HI', 'Devel Block', 'Reproductive HI', 'Repro Block',
               'Kidney HI', 'Kidney Block', 'Ocular HI', 'Ocular Block', 'Endocrine HI',
               'Endo Block', 'Hematological HI', 'Hema Block', 'Immunological HI',
               'Immun Block', 'Skeletal HI', 'Skel Block', 'Spleen HI', 'Spleen Block',
               'Thyroid HI', 'Thyroid Block', 'Whole body HI', 'Whole Body Block', 'Cancer Incidence',
               'Met Station', 'Distance to Met Station (km)', 'Facility Center Lat', 'Facility Center Lon',
               'Rural or Urban']
        MaxRisk = df_max_can['MIR (in a million)'].max()  
        
        # Find all risk metric columns with at least one nonzero value
        allmets = ['MIR (in a million)', 'Respiratory HI', 'Liver HI','Neurological HI','Developmental HI',
                    'Reproductive HI', 'Kidney HI', 'Ocular HI', 'Endocrine HI', 'Hematological HI',
                    'Immunological HI','Skeletal HI', 'Spleen HI', 'Thyroid HI', 'Whole body HI']
        nonzero_columns = df_max_can.columns[df_max_can.apply(lambda x: x != 0).any()]
        nonzero_metrics = list(nonzero_columns.intersection(allmets))
        
        
        # Define center coordinates of facilities and find their count; find bounds
        cenlat = (df_max_can['Facility Center Lat'].max() + df_max_can['Facility Center Lat'].min())/2
        cenlon = (df_max_can['Facility Center Lon'].max() + df_max_can['Facility Center Lon'].min())/2
        center = [cenlat, cenlon]
        numFacs = df_max_can['Facility'].count()
        
        southWest_lat = df_max_can['Facility Center Lat'].min()
        southWest_lng = df_max_can['Facility Center Lon'].min()
        northEast_lat = df_max_can['Facility Center Lat'].max()
        northEast_lng = df_max_can['Facility Center Lon'].max()
        mapbounds = [[southWest_lat, southWest_lng], [northEast_lat, northEast_lng]]
        
        try:
        
            
            # Create dataframe of cancer risk drivers
            fname = self.SCname + "_cancer_drivers.xlsx"
            canc_driv_file = os.path.join(self.dir, fname)
            dataTypes2 = {'Facility ID':str, 'Source ID': str}
            df_canc_driv_temp = pd.read_excel(canc_driv_file, dtype=dataTypes2,
                                         usecols = ('A,B,C,D,F'))
            df_canc_driv = df_canc_driv_temp.loc[(df_canc_driv_temp['MIR']>=5E-7) & (df_canc_driv_temp['Cancer Risk'] >= .1 * df_canc_driv_temp['MIR'])].copy()
            df_canc_driv['Source/Pollutant Risk_MILL'] = df_canc_driv['Cancer Risk']*1000000
            df_canc_driv.columns = ['Facility', 'Facility MIR', 'Pollutant', 'S/P Risk', 'Source ID', 'Source/Pollutant Risk']
            df_canc_driv['Pollutant'] = df_canc_driv['Pollutant'].str.title()
#            df_canc_driv['Facility']= df_canc_driv['Facility'] = 'F' + df_canc_driv['Facility'].astype(str)
            df_canc_driv.sort_values(by = ['Facility MIR'],ascending = False, inplace = True)
                               
            # Create dataframe of max TOSHI drivers
            fname = self.SCname + "_hazard_index_drivers.xlsx"
            hi_driv_file = os.path.join(self.dir, fname)
            df_max_HI = pd.read_excel(hi_driv_file, dtype=dataTypes2)
            HI_types_formax = list(set(df_max_HI['HI Type']))
            df_max_HI = df_max_HI.loc[(df_max_HI['HI Total'] >= 0.2) & (df_max_HI['Hazard Index'] >= .1 * df_max_HI['HI Total'])].copy()
            df_max_HI['Pollutant'] = df_max_HI['Pollutant'].str.title()
            df_max_HI.sort_values(by = ['HI Total'], ascending = False, inplace = True)
#            df_max_HI.rename(columns={'Facility ID' : 'Facility'})
#            df_max_HI['Facility ID']= df_max_HI['Facility ID'] = 'F' + df_max_HI['Facility ID'].astype(str)
            
            
            
            HI_types = list(set(df_max_HI['HI Type']))
            numTOs = len(HI_types)
            
            MaxHI = df_max_can[HI_types_formax].max(axis=1, skipna =True)
            MaxHIid = df_max_can[HI_types_formax].idxmax(axis=1)
            df_max_can.insert(6, "Max TOSHI", MaxHI)
            df_max_can.insert(7, "Max TOSHI Organ", MaxHIid)
            df_max_can.loc[df_max_can["Max TOSHI"] == 0, "Max TOSHI Organ"] = ''
            Overall_MaxHI = df_max_can["Max TOSHI"].max()
            
            #Creating a df just for the dashtable
            df_dashtable = df_max_can.copy()
                        
            # Create dataframe of pollutant incidence drivers
            fname = self.SCname + "_incidence_drivers.xlsx"
            can_inc_drv = os.path.join(self.dir, fname)
            df_inc_drv_temp = pd.read_excel(can_inc_drv, dtype={'Pollutant': str, 'Incidence': float},
                                       usecols = ('A,B'))
            df_inc_drv = df_inc_drv_temp.dropna()
            TotalInc = df_inc_drv_temp[df_inc_drv_temp.Pollutant=='Total incidence'].Incidence.item()
            df_inc_drv.drop(df_inc_drv.index[df_inc_drv['Pollutant'] == 'Total incidence'], inplace = True)
            df_inc_drv.drop(df_inc_drv.index[df_inc_drv['Incidence'] < TotalInc*0.01], inplace = True)
            df_inc_drv['Pollutant'] = df_inc_drv['Pollutant'].str.title()
            df_inc_drv.columns = ['Pollutant', 'Cancer Incidence']
            
            # Create dataframe of source type incidence drivers
            fname = self.SCname + "_source_type_risk.xlsx"
            can_inc_src_drvFile = os.path.join(self.dir, fname)
            df_inc_src_drv = pd.read_excel(can_inc_src_drvFile, skiprows=1)
            df_inc_src_drv.drop(columns = 'Maximum Overall', inplace=True)
            Inc_row = df_inc_src_drv.loc[df_inc_src_drv['Unnamed: 0']=='Incidence'].copy()
            Inc_row.drop(columns = 'Unnamed: 0', inplace = True)
            Inc_row_melt = pd.melt(Inc_row, var_name = 'Source Type', value_name = 'Incidence',
                                    value_vars = Inc_row.columns)
            Inc_row_melt.drop(Inc_row_melt.index[Inc_row_melt['Incidence'] == 0], inplace = True)
            Inc_row_melt.columns = ['Source Type', 'Cancer Incidence']
             
            # Create dataframe of cancer histogram
            fname = self.SCname + "_histogram_risk.xlsx"
            can_histo_file = os.path.join(self.dir, fname)
            df_can_histo = pd.read_excel(can_histo_file, dtype={'Risk level': str, 'Population': float},
                                       usecols = ('A,B'))
            df_can_histo.columns = ['Risk Level', 'Population']
            df_can_histo = df_can_histo.fillna(0).copy()
            
            # Create dataframe of cancer histogram
            fname = self.SCname + "_hi_histogram.xlsx"
            HI_hist_file = os.path.join(self.dir, fname)
            df_hi_histo = pd.read_excel(HI_hist_file)
            cols = [c for c in df_hi_histo if 'facilities' in c.lower()]
            df_hi_histo.drop(columns=cols, inplace=True)
            df_hi_histo.columns = df_hi_histo.columns.str.replace(' Pop','')
            df_hi_histo_melt= pd.melt(df_hi_histo, id_vars=['HI Level'], var_name = 'Target Organ', value_name = 'Population')
            
            
            #Determine whether to use log or linear scales in graphics
            if (MaxRisk >= 10 * df_max_can['MIR (in a million)'].median()):
                riskScale = 'log'
            else:
                riskScale = 'linear'
                
            if (Overall_MaxHI >= 10 * df_max_can['Max TOSHI'].median()):
                HIScale = 'log'
            else:
                HIScale = 'linear'
            
            # Create a bar chart of risk drivers
            
            if df_canc_driv.empty:
                riskDriv = None
            else:
                riskDriv = px.bar(df_canc_driv, x = 'Facility', y = 'Source/Pollutant Risk',
                                  color = 'Pollutant', barmode = 'relative', hover_data=('Source ID', 'Pollutant'),
                                  text = 'Source ID', height = 600)
                riskDriv.layout.yaxis = {'title': 'Source/Pollutant Risk (in a million)', 'type': riskScale}
                riskDriv.update_layout(title = 'Source and Pollutant Risk Drivers of Max Risk' + ' for ' + self.SCname +
                                       '<br>(facility risk ≥ 0.5 in a million)',
                                       yaxis={'type': riskScale, 'automargin':True},
                                       xaxis={'tickangle':45, 'automargin':True,
                                              'type':'category', 'categoryorder': 'array',
                                              'categoryarray': df_canc_driv['Facility']}
                                       )
                riskDriv.update_xaxes(range = (-.5, min(numFacs,50)))
                
                    
            # Create a bar chart of HI drivers
            
            if df_max_HI.empty:
                HIDriv = None
            else: 
                HIDriv = px.bar(df_max_HI, x="Facility ID", y="Hazard Index", color="Pollutant", barmode="relative",
                                facet_row ="HI Type", text = 'Source ID', height=300*numTOs,
                                opacity=1)
                HIDriv.update_layout(title = 'Source and Pollutant Drivers of Max HI' + ' for ' + self.SCname +
                                     '<br>(facility HI ≥ 0.2)',
                                     yaxis={'type': HIScale, 'automargin':True},
                                     xaxis={'tickangle':45,'automargin':True,
                                            'type':'category', 'categoryorder': 'array',
                                            'categoryarray': df_max_HI['Facility ID']},
                                            xaxis_title="Facility",)
                HIDriv.update_yaxes(matches=None)
                HIDriv.update_xaxes(range = (-.5, min(numFacs,50)))
            
            
            try:
                # Create dataframe of acute HQs
                fname = self.SCname + "_acute_impacts.xlsx"
                acute_file = os.path.join(self.dir, fname)
                df_acute = pd.read_excel(acute_file, dtype=dataTypes2,
                                         usecols = ('A,B,J,K,L,N,O'))
                df_acute.columns = ['Facility', 'Pollutant', 'REL', 'AEGL-1', 'ERPG-1', 'AEGL-2', 'ERPG-2']
                df_acute['Pollutant'] = df_acute['Pollutant'].str.title()
                df_acute_melt = pd.melt(df_acute, id_vars = ['Facility', 'Pollutant'],var_name = 'Reference Value', value_name = 'HQ',
                                        value_vars = ['REL', 'AEGL-1', 'ERPG-1', 'AEGL-2', 'ERPG-2'])
                indexNames = df_acute_melt[ df_acute_melt['HQ'] == 0 ].index
                df_acute_melt.drop(indexNames , inplace=True)
                df_acute_melt= df_acute_melt.loc[df_acute_melt['HQ']>=0.5]
                df_acute_melt.sort_values(by = ['HQ'],ascending = False, inplace = True)
                
                Acute_types = set(df_acute_melt['Reference Value'])
                Acute_pols = set(df_acute_melt['Pollutant'])
                numAcutRefs = len(Acute_types)
                numAcutPols = len(Acute_pols)
                
                if (df_acute_melt.loc[:,'HQ'].max() >= 10 * df_acute_melt.loc[:,'HQ'].median()):
                    acuteScale = 'log'
                else:
                    acuteScale = 'linear' 
                
                # Create bar charts of acute HQs
                acuteBar = px.bar(df_acute_melt, x="Pollutant", y="HQ", color='Reference Value', barmode= 'overlay',
                                opacity = .7, height = 600, hover_name = "Facility", text = 'Facility')
                acuteBar.update_layout(title = 'Acute Screening Hazard Quotients' + ' for ' + self.SCname +
                                       '<br>(for pollutants with HQ ≥ 0.5)',
                                       yaxis={'type': acuteScale},
                                       xaxis={'tickangle':45, 'automargin':True},
                                       )
            except:
                acuteBar = None
            
            #Create a pie chart of cancer incidence by pollutant
            
            if df_inc_drv.empty:
                inc_Pie = None
            else:
                if len(self.SCname) > 15:
                    poll_title = f'Cancer Incidence by Pollutant for <br>{self.SCname}<br>(for pollutants that contribute at least 1%)'
                else:
                    poll_title = f'Cancer Incidence by Pollutant for {self.SCname}<br>(for pollutants that contribute at least 1%)'
                
                inc_Pie = px.pie(df_inc_drv, names = 'Pollutant', values = 'Cancer Incidence',
                                 title = poll_title)
                inc_Pie.update_layout(title={'x' : 0.75, 'xref' : 'container', 'xanchor': 'right'})
            
            #Create a pie chart of cancer incidence by source type
            
            if Inc_row_melt.empty:
                src_inc_Pie = None
            else:
                if len(self.SCname) > 15:
                    src_title = f'Cancer Incidence by Source Type for <br>{self.SCname}'
                else:
                    src_title = f'Cancer Incidence by Source Type for {self.SCname}'
                
                
                src_inc_Pie = px.pie(Inc_row_melt, names = 'Source Type', values = 'Cancer Incidence',
                                 labels = {'Total Incidence': TotalInc},
                                 title = src_title
                                 )
                src_inc_Pie.update_layout(title={'x' : 0.75, 'xref' : 'container', 'xanchor': 'right'})
            
            # Create a cancer histogram
            
            if df_can_histo.empty:
                can_histo = None
            else:
                can_histo = px.bar(df_can_histo, x = 'Risk Level', y = 'Population',
                                   
                                   log_y = 'True', text= '{:}'.format('Population'),
                                   title = 'Cancer Population Risks' + ' for ' + self.SCname)
            
            # Create a noncancer histogram
            
            if df_hi_histo_melt.empty:
                hi_histo = None
            else:
                hi_histo = px.bar(df_hi_histo_melt, x="HI Level", y="Population", color="Target Organ", barmode="group",
                                log_y=True, text= "{}".format("Population"))
                hi_histo.update_layout(title = 'NonCancer Population Risks' + ' for ' + self.SCname)
                hi_histo.update_xaxes(autorange="reversed")
            
            
            # Create layout of the app
            # The config code modifies the dcc graph objects
            
            chart_config = {'modeBarButtonsToRemove': ['toggleSpikelines','hoverCompareCartesian', 'lasso2d', 'select2d'],
                            'doubleClickDelay': 1000,
                            'toImageButtonOptions': {
                                'format': 'png', # one of png, svg, jpeg, webp
                                'filename': 'HEM Results ' + self.SCname,
                                'width': 1100,
                                'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
                                }
                            }
            
            HIDriv_config = {'modeBarButtonsToRemove': ['toggleSpikelines','hoverCompareCartesian', 'lasso2d', 'select2d'],
                            'doubleClickDelay': 1000,
                            'toImageButtonOptions': {
                                'format': 'png', # one of png, svg, jpeg, webp
                                'filename': 'HEM Results ' + self.SCname,
                                'width': 1100,
                                'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
                                }
                            }
            
            #Here, if the dataframe for the graph is empty, don't make a graph

            if riskDriv is None:
                riskdriv_dcc = ''
            else:
                riskdriv_dcc = dcc.Graph(figure = riskDriv, config = chart_config, style = {'height': 600})
                
            if HIDriv is None:
                HIDriv_dcc = ''
            else:
                HIDriv_dcc = dcc.Graph(figure = HIDriv, config = HIDriv_config, style = {'height': numTOs*300})
                
            try:
                acute_dcc = dcc.Graph(figure = acuteBar, config = chart_config, style = {'height': 600})
            except:
                acute_dcc = ''    
                
            if inc_Pie is None:
                pollinc_dcc = ''
            else:
                pollinc_dcc = dcc.Graph(figure = inc_Pie, config = chart_config)    
                
            if src_inc_Pie is None:
                srcinc_dcc = ''
            else:
                srcinc_dcc = dcc.Graph(figure = src_inc_Pie, config = chart_config)    
                
            if can_histo is None:
                canhisto_dcc = ''
            else:
                canhisto_dcc = dcc.Graph(figure = can_histo, config = chart_config, style = {'height': 600})    
                
            if hi_histo is None:
                hihisto_dcc = ''
            else:
                hihisto_dcc = dcc.Graph(figure = hi_histo, config = chart_config, style = {'height': 600}) 
            
            
            #Reformatting columns because dashtable does not sort scientific notation
            # for column in cols2format_E  +  cols2format_f:
            #     df_dashtable[column] = df_dashtable[column].map(lambda x: '{:.6f}'.format(x))
            
            
            blue_scale = ['#bce6f9', '#74bbed', '#4d96ce', '#48799d', '#404d54']
            # blue_scale = ['aliceblue', 'darkblue']
            green_scale = ['#cbf6d9', '#64d2a2', '#33b581', '#368165', '#39544c']
            red_scale = ['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15']
            orange_scale = ['#ffa200', '#ff6e00', '#c85700', '#914505', '#582c0e']
            blue_to_red = ['#2b83ba', '#abdda4', '#ffffbf', '#fdae61', '#d7191c']
            red_to_blue = ["#d7191c", "#fdae61", "#ffffbf", "#abdda4", "#2b83ba"]
            blue_to_yellow =["#3a4d6b", "#3d6da2", "#799a96", "#ccbe6a", "#ffec99"]
            yellow_to_blue = ['#ffec99', '#ccbe6a', '#799a96', '#3d6da2', '#3a4d6b']
            purple_to_yellow = ['purple', 'yellow']
            yellow_to_purple = ['yellow', 'purple']

            facramps = {'Purple to Yellow': purple_to_yellow, 'Yellow to Purple': yellow_to_purple,
                        'Blue to Yellow': blue_to_yellow, 'Yellow to Blue': yellow_to_blue,
                        'Blue to Red': blue_to_red, 'Red to Blue': red_to_blue,  
                        'Green Scale': green_scale, 'Orange Scale': orange_scale,'Red Scale': red_scale,
                        'Blue Scale' : blue_scale}
            
            # Create geobuf of state boundaries for facility map
            with open('assets/states_lines.geojson') as f:
                statejson = json.load(f)
            statebuf = dlx.geojson_to_geobuf(statejson)
                    
            
            app.layout = html.Div([

#                    dcc.Interval(id='interval1', interval=5 * 1000, n_intervals=0),
#                    html.H1(id='label1', children=''),

# Mark commented these out
#                dcc.Input(id="input1", type="hidden", value="shutdown"),
#                dcc.Input(id="input2", type="hidden"),
                
                html.Div([
                        # html.Hr(),    
                        html.H2("HEM Summary Results for " + self.SCname + " Model Run", style={'text-align':'center', 'font-weight': 'bold'}),
                        # html.Hr(),
                        ]),
            
            dcc.Tabs([
                    
                dcc.Tab(label="Facility Map", children=[
                    
                    html.Div([
                    
                    dbc.Container([
                    
                        
                        ###########  Start Map Dropdowns  ##########
                    dbc.Row([
                        
                        dbc.Col([
                            
                            html.Hr(),
                            html.H6("Risk metric"),
                              dcc.Dropdown(id='facs_metdrop',
                                           
                                          options=[{"label": i, "value": i} for i in nonzero_metrics],
                                          multi=False,
                                          clearable=False,
                                          value = nonzero_metrics[0],
                                          placeholder="Select a Metric",
                                          ),
                              dbc.Tooltip(                        
                                  [html.P('Risk metrics with all zero values are not included in this dropdown menu')],
                                  target='facs_metdrop',
                                  trigger = 'click hover focus legacy',
                                  style={'backgroundColor': '#FFFFFF',
                                         'opacity': '1.0',
                                         'borderRadius': '4px'},
                                  class_name="fw-bold"
                              ),
                            
                            html.Hr(),
                            html.H6("Color ramp"),  
                              dcc.Dropdown(id='facs_rampdrop',
                                           
                                          options=[{"label": key, "value": key} for (key,value) in facramps.items()],
                                          multi=False,
                                          clearable=False,
                                          value = 'Purple to Yellow',
                                          placeholder="Select a Color Ramp",
                                          ),
                            
                            html.Hr(),
                            html.H6("Dot size"),  
                              dcc.Dropdown(id='facs_sizedrop',
                                           
                                          options=[{"label": i, "value": i} for i in range(3,16)],
                                          multi=False,
                                          clearable=False,
                                          value = 5,
                                          placeholder="Select a Dot Size",
                                          ),
                        ], width = 2),
                        
                        
                        dbc.Col([
                                                        
                            html.H5(id='facs-map-title'),
                            
                            dl.Map(id="tab1-map", center=[39.8283, -97], zoom = 4, minZoom = 3, zoomSnap = .3, bounds=mapbounds,
                                    children = [                                    
                                        
                                         dl.LayersControl([ct_esri, ct_dark, ct_light, ct_openstreet] +                                                                
                                                                                        
                                                 [
                                                     
                                                ct_roads, ct_places,
                                               
                                                dl.Overlay(
                                                dl.GeoJSON(                                                                                              
                                                    id='facs_layer',
                                                    format='geobuf',                                           
                                                    # hoverStyle=arrow_function(dict(weight=5, color='#666'))
                                                    ),
                                                name = 'Facilities', checked = True
                                                ),
                                                
                                                dl.Overlay(
                                                    dl.GeoJSON(id = 'statesid', format="geobuf",
                                                                   data=statebuf,
                                                                   # hoverStyle=arrow_function(dict(weight=1.5, fillColor = 'rgb(0,0,0,0)')),
                                                                   zoomToBoundsOnClick=False,
                                                                  options = dict(weight = .4, fillColor = 'rgb(0,0,0,0)', color = 'beige'),
                                                                   zoomToBounds = False
                                                                   ),
                                               name = 'US States', checked = True
                                               ),
                                                    
                                                    
                                                 
                                                ]
                                                
                                         ),
                                                                                        
                                                 dl.Colorbar(id='facs_colorbar', position="bottomleft", width=20, height=150, nTicks=3, style=dict(background='white')),
                                                
                                                 dl.MeasureControl(position="topleft", primaryLengthUnit="kilometers", primaryAreaUnit="hectares", activeColor="#214097", completedColor="#972158"),
                                    ],                                                                                                           
                                                         
                                    style={'width': '1200px', 'height': '600px'}
                                    )
                        ], width = 9)
                                                           
                    ])
                    
                    ], fluid=True, style={"height": "90vh"})
                                            
                ], style={'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}),
                                    
                ]),
                
                dcc.Tab(label="Cancer Incidence",children=[
                    
                    html.Div([
                        html.Hr(),
                        html.H4("Cancer Incidence by Pollutant and Source Type", style={'font-weight': 'bold'}),
                        html.H5("(Total Incidence is {0:.2E})".format(TotalInc)),
                        html.Hr()
                    ]),
                
                
                html.Div([
                    html.Div([
                        pollinc_dcc,            
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    
                    html.Div([
                        srcinc_dcc,                       
                    ],style={'width': '48%', 'display': 'inline-block'}),
                    
                ]),
            ]),
                dcc.Tab(label="Population Risks",children=[
            
                    html.Div([
                        html.Hr(),
                        html.H4("Population Risks", style={'font-weight': 'bold'}),
                        html.Hr()
                    ]),
                    
                    
                html.Div([
                    canhisto_dcc,
                    html.Hr(),
                    hihisto_dcc,
                ]),
                
            ]),
            
                dcc.Tab(label="Risk Drivers",children=[
            
                html.Div([
                    html.Hr(),
                    html.H4("Pollutant and Source Risk and HI Drivers (of Max Risk and HI)", style={'font-weight': 'bold'}),
                    html.Hr()
                ]),
                html.Div([
                    riskdriv_dcc,
                    html.Hr(),
                    HIDriv_dcc,
                    
                ], style={'width': '100%'}),
               
            ]),
            
            dcc.Tab(label="Acute Screen",children=[
                    
                html.Div([
                    html.Hr(),
                    html.H4("Acute Screening Estimates", style={'font-weight': 'bold'}),
                    html.Hr(),
                    acute_dcc,
                ]),
            
            ]),
            
            dcc.Tab(label="Summary Table",children=[
                    
                 html.Div([
                    html.Hr(),
                    html.H4("Maximum Risk and HI Data", style={'font-weight': 'bold'}),
                    html.Hr()
                ]),
                
                html.Div([
                        dash_table.DataTable(
                            id='table',
                            columns=[{"name": i, "id": i} for i in df_dashtable.columns],
                            data=df_dashtable.to_dict('records'),
                            style_as_list_view=True,
                            style_table={'width': '100%', 'min-width': '100%', 'height': 500,}, 
                                         # 'overflowX': 'scroll', 'overflowY': 'scroll'},
                            style_data_conditional=[
                                {'if': {'row_index': 'odd'},
                                 'backgroundColor': 'Moccasin'
                                 }],
                            style_header={'color':'#191A1A', 'size':'14', 
                                              'backgroundColor':'LightCyan',
                                              'fontWeight':'bold'
                                              },
                            style_cell={'text-align':'center', 'font-family':'arial', 'font=-size':'x-small',
                                        'minWidth': '150px'},
                            fixed_columns = { 'headers': True, 'data': 1 },
                            fixed_rows={ 'headers': True, 'data': 0 },
                            sort_action = 'native',
                            filter_action = 'native',
                            page_action= 'native',
                            sort_mode = 'multi',
                            export_columns = 'all',
                            export_format = 'xlsx',
                            export_headers = 'display',
                            include_headers_on_copy_paste = True
                            )
                ])   
            
            ]),
            
            ]),
                
            ])
            
            # Callback for the facility map
            @app.callback(Output('facs_layer', 'data'),
                          Output('facs_layer', 'hideout'),
                          Output('facs_layer', 'options'),
                                                    
                          Output('facs_colorbar', 'colorscale'),
                          Output('facs_colorbar', 'min'),
                          Output('facs_colorbar', 'max'),
                          Output('facs_colorbar', 'tickText'),
                                                
                          Output('facs-map-title', 'children'),
                                                                                       
                          Input('facs_metdrop', 'value'),
                          Input('facs_rampdrop', 'value'),
                          Input('facs_sizedrop', 'value'),
                          )
                      
            def make_fac_map (metric, ramp, size):
                
                facs_gdf = gp.GeoDataFrame(df_max_can, geometry=gp.points_from_xy(df_max_can['Facility Center Lon'], df_max_can['Facility Center Lat']))
                facs_gdf[f'Log {metric}'] = np.log10(facs_gdf[metric].replace(0, np.nan)) 
                facs_gdf['tooltip']= '<b>Facility: </b>' + facs_gdf['Facility'] + \
                    f'<br><b>{metric}: </b>' + facs_gdf[f'{metric}'].apply(lambda x: f'{self.riskfig(x, 1)}').astype(str) + \
                    '<br><b>Max NonCancer TOSHI: </b>' + facs_gdf['Max TOSHI'].apply(lambda x: f'{self.riskfig(x, 1)}').astype(str) + \
                    '<br><b>Max NonCancer TOSHI Type: </b>' + facs_gdf['Max TOSHI Organ']
                    #'<br><b>Cancer Risk (in a million): </b>' + facs_gdf['MIR (in a million)'].apply(lambda x: f'{self.riskfig(x, 1)}').astype(str) + \
                facs_geojson = json.loads(facs_gdf.to_json())
                facs_buf = dlx.geojson_to_geobuf(facs_geojson)
                
                
                colorscale = facramps[ramp]
                                
                if (facs_gdf[metric].max() >= 100 * facs_gdf[metric].median()):
                    color_prop = f'Log {metric}'
                    vmin = facs_gdf[color_prop].min()
                    vmin_lin = 10**vmin
                    vmax = facs_gdf[color_prop].max()
                    vmid = (vmax+vmin)/2
                    vmax_lin = 10**vmax            
                    vmid_lin = 10**vmid 
                    
                else:
                    color_prop = metric
                    vmin = facs_gdf[color_prop].min()
                    vmin_lin = vmin
                    vmax = facs_gdf[color_prop].max()
                    vmid = (vmax+vmin)/2
                    vmax_lin = vmax            
                    vmid_lin = vmid                  
                                    
                tick1 = int(self.riskfig(vmin_lin,1)) if vmin_lin >= 1 else self.riskfig(vmin_lin,1)
                tick2 = int(self.riskfig(vmid_lin,1)) if vmid_lin >= 1 else self.riskfig(vmid_lin,1)
                tick3 = int(self.riskfig(vmax_lin,1)) if vmax_lin >= 1 else self.riskfig(vmax_lin,1)
                tickText=[str(tick1), str(tick2), str(tick3)]
                                                    
                maptitle = f'Facility Map ({numFacs} facilities) - {metric}'
                draw_facs = Namespace('HEM_leaflet_functions', 'facs')('draw_facilities') 
                fac_hideout=dict(min=vmin, max=vmax, colorscale=colorscale, circleOptions=dict(fillOpacity=1, stroke=False, radius=size), colorProp=color_prop)
                fac_options = dict(pointToLayer=draw_facs)               
                
                return facs_buf, fac_hideout, fac_options, colorscale, vmin, vmax, tickText, maptitle

# Mark commented these out
#            @app.callback(
#                Output(component_id='input2', component_property='children'),
#                [Input(component_id='input1', component_property='value')]
#            )
#            
#            def check_status(value):
#                self.shutdown()
#                return 'Shutting down server'

               
            # @app.callback(
            #         Output("ctab-offcanvas0", "is_open"),

            #         Input("ctab-open-offcanvas0", "n_clicks"),
            #         State("ctab-offcanvas0", "is_open")
            #         )
            # def toggle_offcanvas0(n1, is_open):
            #     if n1:
            #         return not is_open
            #     return is_open    

                
            return app
        
        except Exception as e:
            messagebox.showinfo("Input Error", e)
 


    def shutdown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        time.sleep(20)
        func()
 
 
