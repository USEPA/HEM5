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


class HEM4dash():
    
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
        # jsFuncs = "assets/HEM_leaflet_functions.js"
        
        ct_esri, ct_dark, ct_light, ct_openstreet, ct_places, ct_roads = get_basemaps() # get basemaps and other layers                
                
        app = dash.Dash(__name__, external_stylesheets=dbc_stylesheets, 
                        external_scripts=[chroma], assets_folder=self.resource_path('assets'))
        app.title = 'HEM4 Summary Results: ' + self.SCname
                
        # Create dataframe of max risks
        fname = self.SCname + "_facility_max_risk_and_hi.xlsx"
        max_rsk_hi = os.path.join(self.dir, fname)
        cols2use = ('A,B,D,E,F,G,H,M,N,Q,R,W,X,AA,AB,AE,AF,AI,AJ,AM,AN,AQ,AR,AU,AV,AY,AZ,BC,BD,BG,BH,BK,BL,BO,BQ,BR,BS,BT,BU,BV')
        #cols2use = ('Facil_id', 'mx_can_rsk', 'can_rcpt_type',
        #       'can_latitude', 'can_longitude', 'can_blk', 'respiratory_hi',
        #       'resp_blk', 'liver_hi', 'liver_blk', 'neurological_hi', 'neuro_blk',
        #       'developmental_hi', 'devel_blk', 'reproductive_hi', 'repro_blk',
        #       'kidney_hi', 'kidney_blk', 'ocular_hi', 'ocular_blk', 'endocrine_hi',
        #       'endo_blk', 'hematological_hi', 'hema_blk', 'immunological_hi',
        #       'immun_blk', 'skeletal_hi', 'skel_blk', 'spleen_hi', 'spleen_blk',
        #       'thyroid_hi', 'thyroid_blk', 'whole_body_hi', 'whole_blk', 'incidence',
        #       'metname', 'km_to_metstation', 'fac_center_latitude', 'fac_center_longitude', 'rural_urban')
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
        # mapmets = ['MIR (in a million)', 'Respiratory HI', 'Liver HI','Neurological HI','Developmental HI',
        #            'Reproductive HI', 'Kidney HI', 'Ocular HI', 'Endocrine HI', 'Hematological HI',
        #            'Immunological HI','Skeletal HI', 'Spleen HI', 'Thyroid HI']
        
        # Define center coordinates of facilities and find their count
        cenlat = (df_max_can['Facility Center Lat'].max() + df_max_can['Facility Center Lat'].min())/2
        cenlon = (df_max_can['Facility Center Lon'].max() + df_max_can['Facility Center Lon'].min())/2
        center = [cenlat, cenlon]
        numFacs = df_max_can['Facility'].count()
        
        try:
        
            
            # Create dataframe of cancer risk drivers
            fname = self.SCname + "_cancer_drivers.xlsx"
            canc_driv_file = os.path.join(self.dir, fname)
            dataTypes2 = {'Facility ID':str, 'Source ID': str}
            df_canc_driv_temp = pd.read_excel(canc_driv_file, dtype=dataTypes2,
                                         usecols = ('A,B,C,D,F'))
            df_canc_driv = df_canc_driv_temp.loc[(df_canc_driv_temp['MIR']>=5E-7) & (df_canc_driv_temp['Cancer Risk'] >= .1 * df_canc_driv_temp['MIR'])]
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
            df_max_HI = df_max_HI.loc[(df_max_HI['HI Total'] >= 0.2) & (df_max_HI['Hazard Index'] >= .1 * df_max_HI['HI Total'])]
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
            Inc_row = df_inc_src_drv.loc[df_inc_src_drv['Unnamed: 0']=='Incidence']
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
            df_can_histo = df_can_histo.fillna(0)
            
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
                pass
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
                pass
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
                pass
            
            #Create a pie chart of cancer incidence by pollutant
            
            if df_inc_drv.empty:
                pass
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
                pass
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
                pass
            else:
                can_histo = px.bar(df_can_histo, x = 'Risk Level', y = 'Population',
                                   
                                   log_y = 'True', text= '{:}'.format('Population'),
                                   title = 'Cancer Population Risks' + ' for ' + self.SCname)
            
            # Create a noncancer histogram
            
            if df_hi_histo_melt.empty:
                pass
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
                                'filename': 'HEM4 Results ' + self.SCname,
                                'width': 1100,
                                'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
                                }
                            }
            
            HIDriv_config = {'modeBarButtonsToRemove': ['toggleSpikelines','hoverCompareCartesian', 'lasso2d', 'select2d'],
                            'doubleClickDelay': 1000,
                            'toImageButtonOptions': {
                                'format': 'png', # one of png, svg, jpeg, webp
                                'filename': 'HEM4 Results ' + self.SCname,
                                'width': 1100,
                                'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
                                }
                            }
            
            #Here, if the dataframe for the graph is empty, don't make a graph

            if df_canc_driv.empty:
                riskdriv_dcc = ''
            else:
                riskdriv_dcc = dcc.Graph(figure = riskDriv, config = chart_config, style = {'height': 600})
                
            if df_max_HI.empty:
                HIDriv_dcc = ''
            else:
                HIDriv_dcc = dcc.Graph(figure = HIDriv, config = HIDriv_config, style = {'height': numTOs*300})
                
            try:
                acute_dcc = dcc.Graph(figure = acuteBar, config = chart_config, style = {'height': 600})
            except:
                acute_dcc = ''    
                
            if df_inc_drv.empty:
                pollinc_dcc = ''
            else:
                pollinc_dcc = dcc.Graph(figure = inc_Pie, config = chart_config)    
                
            if df_inc_src_drv.empty:
                srcinc_dcc = ''
            else:
                srcinc_dcc = dcc.Graph(figure = src_inc_Pie, config = chart_config)    
                
            if df_can_histo.empty:
                canhisto_dcc = ''
            else:
                canhisto_dcc = dcc.Graph(figure = can_histo, config = chart_config, style = {'height': 600})    
                
            if df_hi_histo.empty:
                hihisto_dcc = ''
            else:
                hihisto_dcc = dcc.Graph(figure = hi_histo, config = chart_config, style = {'height': 600}) 
            
            
            #Reformatting columns because dashtable does not sort scientific notation
            # for column in cols2format_E  +  cols2format_f:
            #     df_dashtable[column] = df_dashtable[column].map(lambda x: '{:.6f}'.format(x))
            
            # These are for the facility map tab
            facs_mapmets = ['MIR (in a million)', 'Respiratory HI', 'Liver HI', 'Neurological HI',
            'Developmental HI', 'Reproductive HI', 'Kidney HI', 'Ocular HI',
            'Endocrine HI', 'Hematological HI', 'Immunological HI', 'Skeletal HI',
            'Spleen HI', 'Thyroid HI', 'Whole body HI']

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
            
            # These are for the contour map tab
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
        
            
            app.layout = html.Div([

#                    dcc.Interval(id='interval1', interval=5 * 1000, n_intervals=0),
#                    html.H1(id='label1', children=''),

# Mark commented these out
#                dcc.Input(id="input1", type="hidden", value="shutdown"),
#                dcc.Input(id="input2", type="hidden"),
                
                html.Div([
                        # html.Hr(),    
                        html.H2("HEM4 Summary Results for " + self.SCname + " Model Run", style={'text-align':'center', 'font-weight': 'bold'}),
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
                                           
                                          options=[{"label": i, "value": i} for i in facs_mapmets],
                                          multi=False,
                                          clearable=False,
                                          value = 'MIR (in a million)',
                                          placeholder="Select a Metric",
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
                            
                            dl.Map(id="tab1-map", center=[39.8283, -97], zoom = 4, minZoom = 3, zoomSnap = .3,
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
                
                dcc.Tab(label = "Contour Maps", children = [
                    
                    html.Div([
                    
                    dbc.Container([
                        
                            dcc.Store(id='ctab-store-rawdata'),
                            dcc.Store(id='ctab-store-metricdata'),
                            dcc.Store(id='ctab-store-facid'),
                                    
                            dbc.Row([
                                
                                dbc.Col([
                                    dcc.Loading([
                                        
                                        html.H5('Select files to create contours', id='ctab-map-title')
                                        
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
                                    
                                    # html.Br(),
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
                                                                    html.Label(["Download contours as shapefile"]),
                                                                    
                                                                    html.Label(["Download receptor data as csv file"]),
                                                                    
                                                                                                                                                                
                                                                    ], width = 12, className="opacity-100"),
                                                            
                                                                    
                                                    ], className="opacity-100"),    
                                                    
                                                    id="ctab-offcanvas0",
                                                    is_open=False,
                                                ),
                                                                
                                    ], width = 2),
                    
                                
                                dbc.Col([
                                                                                                
                                        dl.Map(id = 'ctab-themap', center = [39., -97.3], minZoom = 3, zoomSnap = .3,
                                                zoom=5, children=[
                                                    dl.LayersControl([ct_esri, ct_dark, ct_light, ct_openstreet],)
                                                    ],
                                                style={'width': '1200px', 'height': '600px'}),
                                                                                
                                        ], width=10)
                                                         
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
                
                                    
                color_prop = f'Log {metric}'
                colorscale = facramps[ramp]
                    
                vmin = facs_gdf[color_prop].min()
                vmin_lin = 10**vmin
                tick1 = int(self.riskfig(vmin_lin,1)) if vmin_lin >= 1 else self.riskfig(vmin_lin,1)
                vmax = facs_gdf[color_prop].max()
                vmid = (vmax+vmin)/2
                vmax_lin = 10**vmax            
                vmid_lin = 10**vmid            
                tick2 = int(self.riskfig(vmid_lin,1)) if vmid_lin >= 1 else self.riskfig(vmid_lin,1)
                tick3 = int(self.riskfig(vmax_lin,1)) if vmax_lin >= 1 else self.riskfig(vmax_lin,1)
                tickText=[str(tick1), str(tick2), str(tick3)]
                                    
                maptitle = f'Facility Map ({numFacs} facilities) - {metric}'
                draw_facs = Namespace('HEM_leaflet_functions', 'facs')('draw_facilities') 
                # draw_facs = Namespace(jsFuncs, 'facs')('draw_facilities')                            
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


# Callbacks for the contours tab
            @app.callback(
                       Output('ctab-metric-alert-div', 'children'),
                       Output('ctab-themap', 'children'),
                       Output('ctab-map-title', 'children'),
                       Output('ctab-themap', 'zoom'),
                       Output('ctab-themap', 'center'),
                      
                      Input('ctab-store-metricdata', 'data'),
                      Input('ctab-metricdrop','value'),
                      Input('ctab-classinput', 'value'),
                      Input('ctab-opacdrop', 'value'),
                      Input('ctab-classesdrop', 'value'),
                      Input('ctab-rampdrop', 'value'),
                      Input('ctab-sigfigdrop', 'value'),
                      Input('ctab-store-facid', 'data'),
                      Input('ctab-upload-data', 'filename')
                     
                      )
            
            def interp_contour(metdata, metric, usercls, opac, numclass, ramp, digz, facname, filelist):
                        
                if metdata is None:
                    return no_update, no_update, no_update, no_update, no_update
                else:
                    ctx = callback_context
                    comp_id = ctx.triggered[0]['prop_id'].split('.')[0]
                    dfpl = pd.DataFrame(metdata)
                            
                    if dfpl[metric].max() == 0:
                        alert = self.make_alert('There are no nonzero values for this metric')
                        return alert, no_update, no_update, no_update, no_update
                    else:
                        gdf = gp.GeoDataFrame(
                            dfpl, geometry=gp.points_from_xy(dfpl.Longitude, dfpl.Latitude), crs="EPSG:4326")
                        
                        if metric == 'MIR':
                            maptitle = html.H4(f'Facility {facname} - Lifetime Cancer Risk (in a million)')
                            gdf['tooltip'] = '<b>Receptor ID: </b>' + gdf['RecID'] + '<br><b>Cancer Risk (in a million): </b>' + gdf[metric].apply(lambda x: f'{self.riskfig(x, digz)}').astype(str)
                        else:
                            gdf['tooltip'] = '<b>Receptor ID: </b>' + gdf['RecID'] + f'<br><b>{metric}: </b>' + gdf[metric].apply(lambda x: f'{self.riskfig(x, digz)}').astype(str)
                            maptitle = html.H4(f'Facility {facname} - {metric}')
                        
                        # Create separate layers for polar and block receptors
                        polar_recpts = gdf[gdf['RecID'].apply(lambda x: 'ang' in x)]
                        polar_recpts['Distance (m)'] = [x.split('ang')[0] for x in polar_recpts['RecID']]
                        polar_recpts['Angle (deg)'] = [x.split('ang')[1] for x in polar_recpts['RecID']]
                        block_recpts = gdf[gdf['RecID'].apply(lambda x: 'ang' not in x)]
                        
                        if polar_recpts is not None and len(polar_recpts) != 0:
                            polarjson = json.loads(polar_recpts.to_json())
                            polarbuf = dlx.geojson_to_geobuf(polarjson)
                            
                        else:
                            polarbuf = None
                            
                        if block_recpts is not None and len(block_recpts) != 0:
                            blockjson = json.loads(block_recpts.to_json())
                            blockbuf = dlx.geojson_to_geobuf(blockjson)
                                                        
                        else:
                            blockbuf = None                       
                        
                        # Use the max receptor to center the map
                        max_x = dfpl.loc[dfpl[metric].idxmax()]
                        avglat = max_x['Latitude'] 
                        avglon = max_x['Longitude']
                                    
                        # 
                        halfgrid_m = 20000
                        res_m = 10
                        halfgrid = halfgrid_m/111133
                        res = res_m/111133
                        numcells = round(halfgrid*2/res)
                                            
                        gdfBounds = gdf.bounds
                        
                    
                        ''' Create the meshgrid to which to interpolate
                        '''
                        x_coord = np.linspace(avglon - halfgrid, avglon + halfgrid, numcells)
                        y_coord = np.linspace(avglat - halfgrid, avglat + halfgrid, numcells)
                        x_grid, y_grid = np.meshgrid(x_coord, y_coord)
                                
                        ''' Use scipy griddata interpolation on the meshgrid
                        '''
                        scigrid = griddata((gdfBounds.minx.to_numpy(), gdfBounds.miny.to_numpy()), gdf[metric].to_numpy(),
                                            (x_grid, y_grid), method = 'linear', rescale=True)
                        
                        blockf = [True for i in filelist if 'block' in i]
                        if blockf and blockf[0] == True and len(blockf) == 1:
                            datamin = gdf[metric].min()
                        else:
                            datamin = scigrid.min()
                        datamax = gdf[metric].max()
                        
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
                            
                            for item in finuserlist:
                                if item > datamax or item < datamin:
                                    finuserlist.remove(item)
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
                    
                        cont_json = geojsoncontour.contourf_to_geojson(
                            contourf=gridcontour,
                            ndigits=5,
                            unit='',
                            min_angle_deg = .00001
                        )
                        
                        
                        loadcont=json.loads(cont_json)
                        contgdf=gp.GeoDataFrame.from_features(loadcont)
                        contgdf['assgnvals'] = levels[1:]
                        classes = contgdf.assgnvals.to_list()
                        contgdf['assgnvals'] = contgdf['assgnvals']*1.05
                        contgdf.set_crs('epsg:4326')
                        gdfJSON = contgdf.to_json()
                                    
                        
                        polydata = json.loads(gdfJSON)
                        colorscale = contgdf.fill.to_list()
                        style=dict(weight=1, opacity=1, color='white', fillOpacity=opac)
                                    
                        ctg=[]
                                   
                        for i, val in enumerate(classes):
                            
                            if i == 0:
                                ctg.append(f'<b>{self.riskfig(lowend, digz)} - {self.riskfig(val, digz)}</b>')
                            else:
                                levbot = classes[i-1]
                                ctg.append(f'<b>{self.riskfig(levbot, digz)} - {self.riskfig(val, digz)}</b>')
                                                
                        
                        # cont_style = Namespace(jsFuncs, 'contour')('draw_contours')
                        # draw_blocks = Namespace(jsFuncs, 'contour')('draw_block_receptors')
                        # draw_polars = Namespace(jsFuncs, 'contour')('draw_polar_receptors')
                        cont_style = Namespace('HEM_leaflet_functions', 'contour')('draw_contours')
                        draw_blocks = Namespace('HEM_leaflet_functions', 'contour')('draw_block_receptors')
                        draw_polars = Namespace('HEM_leaflet_functions', 'contour')('draw_polar_receptors2')
                        # draw_cluster = Namespace('HEM_leaflet_functions', 'contour')('draw_cluster')
                        
                        cont_hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp='assgnvals')
                                                
                        contmap = [
                            
                                dl.MeasureControl(position="topleft", primaryLengthUnit="meters", primaryAreaUnit="hectares",
                                                             activeColor="#214097", completedColor="#972158"),
                            
                                dl.LayersControl([ct_esri, ct_dark, ct_light, ct_openstreet] +
                                                 
                                                  [
                                                                                                            
                                                      dl.Overlay(
                                                            
                                                             dl.LayerGroup(
                                                             dl.GeoJSON(id = 'ctab-blocks', format="geobuf",
                                                                        data=blockbuf,
                                                                        # cluster=True, 
                                                                        # zoomToBoundsOnClick=True,
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
                                                     
                                                     ct_roads, ct_places
                                                                                     
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
                        
                        return no_update, contmap, maptitle, zoom, center


            # This callback takes the csv file(s) loaded by user and creates a dataframe
            @app.callback(Output('ctab-store-rawdata', 'data'),
                          Output('ctab-upload-alert-div', 'children'),
                          Output('ctab-store-facid', 'data'),
                                                      
                          Input('ctab-upload-data', 'filename'),
                          Input('ctab-upload-data', 'contents'),
                         )
            
            def store_rawdata(filelist, contents):
                                
                if filelist is None:
                    alert = no_update
                    data = no_update
                    facname = no_update
                                    
                else:
                    if len(filelist) > 2:
                        alert = self.make_alert("Only load 1 or 2 files")
                        data = no_update
                        facname = no_update
                                                
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
                            
                        elif len(goodnames) == 2 and (goodnames[0].split('_')[0] != goodnames[1].split('_')[0]):
                            alert =self.make_alert("Facility names for the files don't match")
                            data = no_update
                            facname = no_update
                                    
                        else:
                            dflist =[]
                            for i, item in enumerate(goodnames):
                                # currfile = goodnames[i]
                                currcontent = goodcontents[i]
                                content_type, content_string = currcontent.split(',')
                                decoded = base64.b64decode(content_string)
                                dtype={"FIPs": str, "Block": str}
                                currdf = pd.read_csv(io.StringIO(decoded.decode('utf-8')), dtype = dtype)
                                currdf.rename(columns={'Distance (m)': 'dist', 'Angle (from north)': 'angle'}, inplace=True)
                                
                                if 'angle' in currdf.columns:
                                    currdf['RecID'] = currdf.dist.astype(str).str.cat(currdf.angle.astype(str), sep='ang')
                                else:
                                    currdf['RecID'] = currdf.FIPs.astype(str).str.cat(currdf.Block.astype(str))
                                
                                tempdf = currdf.copy()
                                tempdf['MIR'] = tempdf['MIR']*1000000
                                
                                # Limit the number of block receptors (don't need so many nor so far out)
                                if 'block_summary_chronic.csv' in item:
                                                                        
                                    try:
                                        for metric in metrics:
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
                                    
                                    delta = .1
                                    finaldf = tempdf[tempdf['Latitude'].between(midlat-delta, midlat+delta) & tempdf['Longitude'].between(midlon-delta, midlon+delta)]
                                else:
                                    finaldf = tempdf.copy()
                                                 
                                dflist.append(finaldf)
                               
                                
                            alldfs = pd.concat(dflist)
                                                
                            alert=no_update
                            data = alldfs.to_dict('records')
                                            
                    return data, alert, facname
                
                
            # Take the df of the concatenated raw data and trim down the columns to chosen metric               
            @app.callback(Output('ctab-store-metricdata', 'data'),
                                                      
                          Input('ctab-store-rawdata', 'data'),
                          Input('ctab-metricdrop', 'value')
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
                        dff = dff[['RecID', 'Latitude', 'Longitude', metric]]
                                   
                        outdata = dff.to_dict('records')
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

                
            return app
        
        except Exception as e:
            messagebox.showinfo("Input Error", e)
 


    def shutdown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        time.sleep(20)
        func()
 
 