# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 23:29:19 2019

@author: David Lindsey
"""

import tkinter as tk
import webbrowser
import tkinter.ttk as ttk
from functools import partial
import shutil


from PyQt5 import QtGui
from pandastable import Table, filedialog, np
from datetime import datetime
from com.sca.hem4.log.Logger import Logger
from com.sca.hem4.tools.CensusUpdater import CensusUpdater
from com.sca.hem4.model.Model import Model
from com.sca.hem4.upload.FileUploader import FileUploader
from tkinter.filedialog import askopenfilename
from com.sca.hem4.DepositionDepletion import check_dep, check_phase
from com.sca.hem4.SaveState import SaveState
from tkinter.simpledialog import Dialog, Toplevel
from com.sca.hem4.GuiThreaded import Hem4
from com.sca.hem4.writer.excel.FacilityMaxRiskandHI import FacilityMaxRiskandHI
from com.sca.hem4.log import Logger
from concurrent.futures import ThreadPoolExecutor
import threading
from tkinter import messagebox
from tkinter import scrolledtext
import pickle

from com.sca.hem4.runner.FacilityRunner import FacilityRunner
from com.sca.hem4.writer.excel.FacilityCancerRiskExp import FacilityCancerRiskExp
from com.sca.hem4.writer.excel.FacilityTOSHIExp import FacilityTOSHIExp
from com.sca.hem4.writer.kml.KMLWriter import KMLWriter
from com.sca.hem4.inputsfolder.InputsPackager import InputsPackager

import traceback
from collections import defaultdict


import queue

import os
import glob
import importlib 

from PIL import ImageTk
import PIL.Image
import pandas as pd

maxRiskReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.MaxRisk")
cancerDriversReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.CancerDrivers")
hazardIndexDriversReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.HazardIndexDrivers")
histogramModule = importlib.import_module("com.sca.hem4.writer.excel.summary.Histogram")
hiHistogramModule = importlib.import_module("com.sca.hem4.writer.excel.summary.HI_Histogram")
incidenceDriversReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.IncidenceDrivers")
acuteImpactsReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.AcuteImpacts")
sourceTypeRiskHistogramModule = importlib.import_module("com.sca.hem4.writer.excel.summary.SourceTypeRiskHistogram")
multiPathwayModule = importlib.import_module("com.sca.hem4.writer.excel.summary.MultiPathway")

from com.sca.hem4.summary.SummaryManager import SummaryManager


TITLE_FONT= ("Verdana", 18)
TEXT_FONT = ("Verdana", 14)
SUB_FONT = ("Verdana", 12)

def hyperlink1(event):
    webbrowser.open_new(r"https://www.epa.gov/fera/risk-assessment-and-"+
                        "modeling-human-exposure-model-hem")

def hyperlink2(event):
    webbrowser.open_new(r"https://www.epa.gov/fera/human-exposure-model-hem-3"+
                        "-users-guides")
    




class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()

class Page1(Page):
    
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        self.noteStyler = ttk.Style()
        self.noteStyler.configure("TNotebook", background="alice blue", borderwidth=0)
        self.noteStyler.configure("TNotebook.Tab", background="alice blue", borderwidth=0)
        self.noteStyler.configure("TFrame", background="alice blue", borderwidth=0)

        
        # Tab Control introduced here --------------------------------------
        self.tabControl = ttk.Notebook(self, style='TNotebook')     # Create Tab Control
        
        self.container = tk.Frame(self, bg="alice blue")
#        self.buttonframe.pack(side="right", fill="y", expand=False)
        
        self.s=ttk.Style()
        print(self.s.theme_names())
        self.s.theme_use('clam')
        
        
        self.tabControl.add(self.container, text='Summaries')      # Add the tab

        self.log2 = tk.Frame(self.tabControl, bg='alice blue')            # Add a second tab
        self.tabControl.add(self.log2, text='Log')      # Make second tab visible
    
        
        # Adding a Textbox Entry widget
#        scrolW  = 65; scrolH  =  25
        self.scr = scrolledtext.ScrolledText(self.log2, wrap=tk.WORD, width=1000, height=1000, font=TEXT_FONT)
        self.scr.pack()

        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible

         #create grid
        self.s1 = tk.Frame(self.container, width=750, height=100, bg="alice blue")
        self.s2 = tk.Frame(self.container, width=750, height=100, bg="alice blue")
        self.s3 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s4 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s5 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s6 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s7 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s8 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s9 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s10 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s11 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s12 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s13 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="alice blue")

          
        self.s1.grid(row=0)
        self.s2.grid(row=1, column=0)
        self.s3.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.s4.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.s5.grid(row=5, column=0, columnspan=2, sticky="nsew")
        self.s6.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.s7.grid(row=7, column=0, columnspan=2, sticky="nsew")
        self.s8.grid(row=8, column=0, columnspan=2, sticky="nsew")
        self.s9.grid(row=9, column=0, columnspan=2, sticky="nsew")
        self.s10.grid(row=10, column=0, columnspan=2, sticky="nsew")
        self.s11.grid(row=11, column=0, columnspan=2, sticky="nsew")
        self.s12.grid(row=12, column=0, columnspan=2, sticky="nsew")
        self.s13.grid(row=13, column=0, columnspan=2, sticky="nsew")


        self.container.grid_rowconfigure(12, weight=4)
        self.container.grid_columnconfigure(0, weight=1)
        

        
        #title
        title = tk.Label(self.s1, text="Risk Summary", font=TITLE_FONT, bg="alice blue")

        title.grid(row = 1)
        
        #instructions
        instructions = tk.Label(self.s1, text="Select one or more risk summary programs", font=TEXT_FONT, bg="alice blue")
        instructions.grid_columnconfigure(1, weight=1)
        instructions.grid(row=2)
        
         #modeling group label
        group_label = tk.Label(self.s1, font=TEXT_FONT, bg="alice blue", 
                             text="Please identify the location of the HEM4 results to be summarized:")
        group_label.grid(row=3)
        
        #file browse button
        self.mod_group = tk.Button(self.s2, command = self.browse, font=TEXT_FONT, relief='solid', borderwidth=2)
        self.mod_group["text"] = "Browse"
        self.mod_group.grid(row=2, column=0, sticky="E", padx=10)
        
        #output directory path
        self.mod_group_list = tk.StringVar(self.s2)
        self.group_list_man = ttk.Entry(self.s2)
        self.group_list_man["width"] = 100
        self.group_list_man["textvariable"]= self.mod_group_list
        self.group_list_man.grid(row=2, column=1, sticky="W")
       
        
        self.var_m = tk.IntVar()
        self.max_risk = tk.Checkbutton(self.s3, font=TEXT_FONT, bg="alice blue", text="Max Risk Summary", variable=self.var_m)
        self.max_risk.grid(row=1, padx=10, sticky="W")
        
        
        self.var_c = tk.IntVar()
        self.cancer_driver = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="alice blue", text="Cancer Drivers", variable=self.var_c)
        self.cancer_driver.grid(row=1, padx=10, sticky="W")
        
        self.var_h = tk.IntVar()
        self.hazard = tk.Checkbutton(self.s5, font=TEXT_FONT, bg="alice blue", text="Hazard Index Drivers", variable=self.var_h)
        self.hazard.grid(row=1, padx=10, sticky="W")
        
        self.var_hi = tk.IntVar()
        self.hist = tk.Checkbutton(self.s6, font=TEXT_FONT, bg="alice blue", text="Risk Histogram", variable=self.var_hi)
        self.hist.grid(row=1, padx=10, sticky="W")
        
        self.var_hh = tk.IntVar()
        self.hh = tk.Checkbutton(self.s7, font=TEXT_FONT, bg="alice blue", text="Hazard Index Histogram", variable=self.var_hh)
        self.hh.grid(row=1, padx=10, sticky="W")
        
        self.var_i = tk.IntVar()
        self.inc = tk.Checkbutton(self.s8, font=TEXT_FONT, bg="alice blue", text="Incidence Drivers", variable=self.var_i)
        self.inc.grid(row=1, padx=10, sticky="W")
        
        self.var_a = tk.IntVar()
        self.ai = tk.Checkbutton(self.s9, font=TEXT_FONT, bg="alice blue", text="Acute Impacts", variable=self.var_a)
        self.ai.grid(row=1, padx=10, sticky="W")

        self.var_p = tk.IntVar()
        self.mp = tk.Checkbutton(self.s10, font=TEXT_FONT, bg="alice blue", text="Multipathway", variable=self.var_p)
        self.mp.grid(row=1, padx=10, sticky="W")
        
        self.var_s = tk.IntVar()
        self.s = tk.Checkbutton(self.s11, font=TEXT_FONT, bg="alice blue", text="Source Type Risk Histogram", variable=self.var_s, command=self.set_sourcetype)
        self.s.grid(row=1, padx=10, sticky="W")
        
                   
        
        #back button
        back_button = tk.Button(self.s13, text="Back", font=TEXT_FONT, relief='solid', borderwidth=2,
                            command=self.lower)
        back_button.grid(row=0, column=2, sticky="W", padx=5, pady=10)
        
        run_button = tk.Button(self.s13, text="Run Reports", font=TEXT_FONT, relief='solid', borderwidth=2,
                            command= self.run_reports)
        run_button.grid(row=0, column=1, sticky="E", padx=5, pady=10)
        
    def browse(self):
        
        self.fullpath = tk.filedialog.askdirectory()
        #print(fullpath)
        self.mod_group_list.set(self.fullpath)
        
    def set_sourcetype(self):

        if self.var_s.get() == 1:
        
            self.pos = tk.Label(self.s12, font=SUB_FONT, bg="alice blue", text="Enter the position in the source ID where the\n source ID type begins.The default is 1.")
            self.pos.grid(row=1, padx=10, sticky="W")
            
            self.pos_num = ttk.Entry(self.s12)
            self.pos_num["width"] = 5
            self.pos_num.grid(row=1, column=2, padx=10, sticky="W")
        
            self.chars = tk.Label(self.s12, font=SUB_FONT, bg="alice blue", text="Enter the number of characters \nof the sourcetype ID")
            self.chars.grid(row=2, padx=10, sticky="W")
            
            self.chars_num = ttk.Entry(self.s12)
            self.chars_num["width"] = 5
            self.chars_num.grid(row=2, column=2, padx=10, sticky="W")
        
        else:
            if self.pos is not None:
                self.pos.destroy()
                self.pos_num.destroy()
                self.chars.destroy()
                self.chars_num.destroy()
                
                
                
    def run_reports(self):

         executor = ThreadPoolExecutor(max_workers=1)
         future = executor.submit(self.createReports)
         #future.add_done_callback(self.reset_reports)           
        
    def createReports(self,  arguments=None):
        
        
        

        ready= False
        
        #check to see if there is a directory location
                 
        try:
            
            # Figure out which facilities will be included in the report
            skeleton = os.path.join(self.fullpath, '*facility_max_risk_and_hi.xl*')
            fname = glob.glob(skeleton)
            if fname:
                head, tail = os.path.split(fname[0])
                groupname = tail[:tail.find('facility_max_risk_and_hi')-1]
                facmaxrisk = FacilityMaxRiskandHI(targetDir=self.fullpath, filenameOverride=tail)
                facmaxrisk_df = facmaxrisk.createDataframe()
                faclist = facmaxrisk_df['Facil_id'].tolist()
            else:
                Logger.logMessage("Cannot generate summaries because there is no Facility_Max_Risk_and_HI Excel file \
                                  in the folder you selected.")
                ready = False 
          
            
        except:
            
             messagebox.showinfo("No facilities selected",
                "Please select a run folder.")
             
             ready = False
        # Figure out which facilities will be included in the report.
        # Facilities listed in the facility_max_risk_and_hi HEM4 output will be used
        # and the modeling group name is taken from the first part of the filename.
        
        
                
        #get reports and set arguments
        reportNames = []
        reportNameArgs = {}
        if self.var_m.get() == 1:
            reportNames.append('MaxRisk')
            reportNameArgs['MaxRisk'] = None
        if self.var_c.get() == 1:
            reportNames.append('CancerDrivers')
            reportNameArgs['CancerDrivers'] = None
        if self.var_h.get() == 1:
            reportNames.append('HazardIndexDrivers')
            reportNameArgs['HazardIndexDrivers'] = None
        if self.var_hi.get() == 1:
            reportNames.append('Histogram')
            reportNameArgs['Histogram'] = None
        if self.var_hh.get() == 1:
            reportNames.append('HI_Histogram')
            reportNameArgs['HI_Histogram'] = None
        if self.var_i.get() == 1:
            reportNames.append('IncidenceDrivers')
            reportNameArgs['IncidenceDrivers'] = None
        if self.var_a.get() == 1:
            reportNames.append('AcuteImpacts')
            reportNameArgs['AcuteImpacts'] = None
                
        if self.var_s.get() == 1:
            reportNames.append('SourceTypeRiskHistogram')
            #pass position number and character number
            if len(self.pos_num.get()) == 0 or self.pos_num.get() == '0':
                startpos = 1
            else:
                startpos = int(self.pos_num.get()) - 1
            numchars = int(self.chars_num.get())
            reportNameArgs['SourceTypeRiskHistogram'] = [startpos, numchars]          

        if self.var_p.get() == 1:
            reportNames.append('MultiPathway')
            reportNameArgs['MultiPathway'] = None
       

        #add run checks
        if (self.var_m.get() != 1 and 
            self.var_c.get() != 1 and
            self.var_h.get() != 1 and
            self.var_hi.get() != 1 and
            self.var_hh.get() != 1 and
            self.var_i.get() != 1 and
            self.var_a.get() != 1 and
            self.var_s.get() != 1  and
            self.var_p.get() != 1):
            
            messagebox.showinfo("No report selected",
                "Please select one or more report types to run.")
            
            ready = False
        else:
           
            #check if source type has been selected
            if self.var_s.get() == 1:
                if numchars == '' or numchars ==' ' or numchars == None:
                    messagebox.showinfo('Missing sourcetype id characters',
                                        'Please enter the number of characters of the sourcetype ID.')
                
                    ready = False
  
                else:
                    
                    ready = True
                    
            else:
                ready = True
                    
                    
        #if checks have been passed 
        if ready == True:
        
        
            running_message = "Running report on facilities: " + ', '.join(faclist)
            
            self.scr.configure(state='normal')
            self.scr.insert(tk.INSERT, running_message)
            self.scr.insert(tk.INSERT, "\n")
            self.scr.configure(state='disabled')
    
            summaryMgr = SummaryManager(self.fullpath, groupname, faclist)
                    
            #loop through for each report selected
            for reportName in reportNames:
                report_message = "Creating " + reportName + " report."
                
                self.scr.configure(state='normal')
                self.scr.insert(tk.INSERT, report_message)
                self.scr.insert(tk.INSERT, "\n")
                self.scr.configure(state='disabled')
                
                try:
                    args = reportNameArgs[reportName]
                    summaryMgr.createReport(self.fullpath, reportName, args)
                except BaseException as e:
                    Logger.logMessage(str(e))
                
                report_complete = reportName +  " complete."
                self.scr.configure(state='normal')
                self.scr.insert(tk.INSERT, report_complete)
                self.scr.insert(tk.INSERT, "\n")
                self.scr.configure(state='disabled')
                
            self.scr.configure(state='normal')
            self.scr.insert(tk.INSERT, "Summary Reports Complete.")
            self.scr.insert(tk.INSERT, "\n")
            self.scr.configure(state='disabled')
            
            
        if self.var_m.get() == 1:
            self.max_risk.deselect()
        if self.var_c.get() == 1:
            self.cancer_driver.deselect()
        if self.var_h.get() == 1:
           self.hazard.deselect()
        if self.var_hi.get() == 1:
            self.hist.deselect()
        if self.var_hh.get() == 1:
            self.hh.deselect()
        if self.var_i.get() == 1:
            self.inc.deselect()
        if self.var_a.get() == 1:
            self.ai.deselect()
        if self.var_s.get() == 1:
            self.s.deselect()
            #pass position number and character number
            self.pos_num.set('')
            self.chars.num.set('')

        if self.var_p.get() == 1:
           self.mp.deselect()
            
 
#needs work       
#    def reset_reports(self):
#        
#        #reset inputs
#        if self.var_m.get() == 1:
#            self.max_risk.deselect()
#    
    
    def color_config(self, widget, color, event):
         widget.configure(bg=color)

class Page2(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        container = tk.Frame(self, bg="alice blue")
        #        self.buttonframe.pack(side="right", fill="y", expand=False)
        container.pack(side="top", fill="both", expand=True)

        self.s1 = tk.Frame(container, width=600, height=50, bg="alice blue")
        self.s2 = tk.Frame(container, width=600, height=50, bg="alice blue")
        self.s3 = tk.Frame(container, width=600, height=50, pady=5, padx=5, bg="alice blue")
        self.s4 = tk.Frame(container, width=600, height=50, pady=5, padx=5, bg="alice blue")
        self.s5 = tk.Frame(container, width=600, height=50, pady=5, padx=5, bg="alice blue")

        self.s1.pack(fill="x")
        self.s2.pack(fill="x")
        self.s3.pack(fill="x")
        self.s4.pack(fill="x")
        self.s5.pack(fill="x")

        #title in first grid space
        title1 = tk.Label(self.s1, text="HEM4", font=TITLE_FONT, bg="alice blue")
        title1.pack(side="top", pady=20)

        title2 = tk.Label(self.s1, text="Human Exposure Model\n Version 4-Open Source ", font=TEXT_FONT, bg="alice blue")
        title2.pack()


        #some information
        prepared_for = tk.Label(self.s2, text="Prepared for: \nAir Toxics" +
                            " Assessment Group \nU.S. EPA \nResearch Triangle Park, NC 27711",
                             font=TEXT_FONT, bg="alice blue")
        prepared_for.pack(padx=45, pady=30, side="left")


        image1 = ImageTk.PhotoImage(PIL.Image.open('images\smokestack.jpg'))
        ione = tk.Label(self.s3, image=image1)
        ione.image = image1 # keep a reference!
        ione.pack(padx=50, side="left")

        prepared_by = tk.Label(self.s2, text="Prepared by: \nSC&A Incorporated\n" +
                            "1414 Raleigh Rd, Suite 450\nChapel Hill, NC 27517",
                             font=TEXT_FONT, bg="alice blue")
        prepared_by.pack(padx=150, pady=30)

        self.s3top = tk.Frame(self.s3, pady=5, padx=5, bg="alice blue")
        self.s3top.pack(fill="both", expand=True)

        self.s3bottom = tk.Frame(self.s3, pady=5, padx=5, bg="alice blue")
        self.s3bottom.pack(fill="both", expand=True)

        img = PIL.Image.open('images\\usersguides.jpg')
        img = img.resize((400, 230), PIL.Image.ANTIALIAS)
        image2 = ImageTk.PhotoImage(img)
        itwo = tk.Label(self.s3bottom, image=image2)
        itwo.image = image2 # keep a reference!
        itwo.pack(padx=0, pady=0, side="right")

        self.s3topright = tk.Frame(self.s3top, height="30", pady=5, padx=5, bg="alice blue")
        self.s3topright.pack(fill="both")

        self.b1 = tk.Button(self.s3topright, text="Start Menu", font=TEXT_FONT,
                           relief='solid', borderwidth=2, bg='lightgrey', command=self.lift_nav)
        self.b1.bind("<Enter>", partial(self.color_config, self.b1, "white"))
        self.b1.bind("<Leave>", partial(self.color_config, self.b1, "lightgrey"))
        self.b1.pack(padx=10, pady=0, side="right")


        self.s3topleft = tk.Frame(self.s3top, pady=5, padx=5, bg="alice blue")
        self.s3topleft.pack(fill="both", expand=True)

        ## hyperlink
        link_to_site = tk.Label(self.s3topleft, text="EPA HEM4 Webpage (link)",
                               font=TEXT_FONT, bg="alice blue", anchor="e")
        link_to_site.pack(pady=10,fill="x", expand=True)
        link_to_site.bind('<Button-1>', hyperlink1)

        link_to_userguide = tk.Label(self.s3topleft, text="HEM4 User's Guide (link)",
                                      font=TEXT_FONT, bg="alice blue", anchor="e")
        link_to_userguide.pack(fill="x", expand=True)
        link_to_userguide.bind("<Button-1>", hyperlink2)

    def lift_nav(self):
        self.lower()
#        self.b1.destroy()
#        
#        self.b1 = tk.Button(self.buttonframe, text="Back", font=TEXT_FONT, 
#                       relief='solid', borderwidth=2, bg='lightgrey')
#        self.b1.bind("<Enter>", partial(self.color_config, self.b1, "white"))
#        self.b1.bind("<Leave>", partial(self.color_config, self.b1, "lightgrey"))
##        b2 = tk.Button(buttonframe, text="Page 2", command=p2.lift)
##        b3 = tk.Button(buttonframe, text="Page 3", command=p3.lift)
##
#        self.b1.pack(side="bottom", fill="x", padx=5, pady=5)       
#       self.hem4 = hem4
       
            
    def color_config(self, widget, color, event):
        widget.configure(bg=color)

class Page3(Page):
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        container = tk.Frame(self, bg="alice blue")
        #        self.buttonframe.pack(side="right", fill="y", expand=False)
        container.pack(side="top", fill="both", expand=True)

        self.s=ttk.Style()
        print(self.s.theme_names())
        self.s.theme_use('clam')

        #create grid
        self.s1 = tk.Frame(container, width=750, height=100, bg="alice blue")
        self.s2 = tk.Frame(container, width=750, height=100, bg="alice blue")
        self.s3 = tk.Frame(container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s4 = tk.Frame(container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s5 = tk.Frame(container, width=750, height=100, pady=5, padx=5, bg="alice blue")

        self.s1.pack(fill="x")
        self.s2.pack(fill="x")
        self.s3.pack(fill="x")
        self.s4.pack(fill="x")
        self.s5.pack(fill="y")

        #title
        title = tk.Label(self.s1, text="Output viewing and analysis", font=TITLE_FONT, bg="alice blue")
        title.pack(pady=10, side="top")

        button_file = tk.Button(self.s2, text="Open a facility or source category output file",
                                font=TEXT_FONT, relief='solid', borderwidth=2, command=self.browse_button)
        button_maps = tk.Button(self.s3, text="Open a chronic or acute map",
                                font=TEXT_FONT, relief='solid', borderwidth=2, command=self.maps_button)

        button_file.pack(side="left", padx=5, pady=10)
        button_maps.pack(side="left", padx=5, pady=10)

        #back button
        back_button = tk.Button(self.s5, text="Back", font=TEXT_FONT, relief='solid', borderwidth=2,
                                command=self.lower)
        back_button.pack(side="left", padx=5, pady=10)


    def browse_button(self):
        datatypes = {
            "% of Total Incidence": np.str, "aconc": np.float64,
            "Acute Conc (ug/m3)": np.float64, "Acute conc (ug/m3)": np.float64,
            "Aegl_1 1hr (mg/m3)": np.float64, "Aegl_1 8hr (mg/m3)": np.float64,
            "AEGL_1_11H": np.float64, "Aegl_2 1hr (mg/m3)": np.float64,
            "Aegl_2 8hr (mg/m3)": np.float64, "AEGL_2_1H": np.float64,
            "Angle": np.float64, "angle": np.float64,
            "Angle (from north)": np.float64, "Block": np.str,
            "block": np.str, "BLOCK": np.str,
            "Block type": np.str, "can_blk": np.str,
            "can_latitude": np.float64, "can_longitude": np.float64,
            "can_rcpt_type": np.str, "can_rsk_interpltd": np.str,
            "Cancer Risk": np.float64, "Chem, Centroid, or Discrete": np.str,
            "Conc (ug/m3)": np.float64, "Conc rounded (ug/m3)": np.float64,
            "Conc sci (ug/m3)": np.float64, "CONC_MG": np.float64,
            "devel_blk": np.str, "devel_hi_interpltd": np.str,
            "devel_rcpt_type": np.str, "Developmental HI": np.float64,
            "developmental_hi": np.float64, "Distance": np.float64,
            "distance": np.float64, "Distance (in meters)": np.float64,
            "Distance (m)": np.float64, "Dry deposition (g/m2/yr)": np.float64,
            "Elevation (in meters)": np.float64, "Elevation (m)": np.float64,
            "Emission type": np.str, "Emissions (tons/year)": np.float64,
            "Emissions (tpy)": np.float64, "endo_blk": np.str,
            "endo_hi_interptd": np.str, "endo_rcpt_type": np.str,
            "Endocrine HI": np.float64, "endocrine_hi": np.float64,
            "ERPG_1": np.float64, "Erpg_1 (mg/m3)": np.float64,
            "ERPG_2": np.float64, "Erpg_2 (mg/m3)": np.float64,
            "fac_center_latitude": np.float64, "fac_center_longitude": np.float64,
            "Facil_id": np.str, 'Facility_id': np.str, 'facility_id': np.str, 'Facid': np.str, \
            "Facility count": np.int, "Facility ID": np.str,
            'FACNAME': np.str, "FIPS": np.str,
            "FIPs": np.str, "fips": np.str,
            "Fips": np.str, "Fips + Block": np.str,
            "Fraction emitted as particulate matter (%)": np.float64, "Hazard Index": np.float64,
            "hema_blk": np.str, "hema_hi_interptd": np.str,
            "hema_rcpt_type": np.str,
            "Hematological HI": np.float64,
            "HI Level": np.str,
            "HI Total": np.float64,
            "HI Type": np.str,
            "Hill": np.float64,
            "Hill Height (in meters)": np.float64,
            "Hill height (m)": np.float64,
            "HQ": np.float64,
            "HQ_AEGL1": np.float64,
            "HQ_AEGL2": np.float64,
            "HQ_ERPG1": np.float64,
            "HQ_ERPG2": np.float64,
            "HQ_IDLH": np.float64,
            "HQ_REL": np.float64,
            "IDLH_10": np.float64,
            "Idlh_10 (mg/m3)": np.float64,
            "immun_blk": np.str,
            "immun_hi_interptd": np.str,
            "immun_rcpt_type": np.str,
            "Immunological HI": np.float64,
            "immunological_hi": np.float64,
            "incidence": np.float64,
            "Incidence": np.float64,
            "Incidence rounded": np.float64,
            "Is max conc at any receptor interpolated? (Y/N)": np.str,
            "Is max populated receptor interpolated? (Y/N)": np.str,
            "Kidney HI": np.float64,
            "kidney_blk": np.str,
            "kidney_hi": np.float64,
            "kidney_hi_interptd": np.str,
            "kidney_rcpt_type": np.str,
            "km_to_metstation": np.float64,
            "Lat": np.float64,
            "lat": np.float64,
            "latitude": np.float64,
            "Latitude": np.float64,
            "Level": np.str,
            "Liver HI": np.float64,
            "liver_blk": np.str,
            "liver_hi": np.float64,
            "liver_hi_interpltd": np.str,
            "liver_rcpt_type": np.str,
            "Lon": np.float64,
            "lon": np.float64,
            "longitude": np.float64,
            "Longitude": np.float64,
            "Max conc at any receptor (ug/m3)": np.float64,
            "Max conc at populated receptor (ug/m3)": np.float64,
            "metname": np.str,
            "MIR": np.float64,
            "Mrl (mg/m3)": np.float64,
            "mx_can_rsk": np.float64,
            "neuro_blk": np.str,
            "neuro_hi_interpltd": np.str,
            "neuro_latitude": np.float64,
            "neuro_longitude": np.float64,
            "neuro_rcpt_type": np.str,
            "Neurological Facilities": np.int,
            "Neurological HI": np.float64,
            "Neurological Pop": np.int,
            "neurological_hi": np.float64,
            "Notes": np.str,
            "Number people exposed to > 1 Developmental HI": np.int,
            "Number people exposed to > 1 Endocrinological HI": np.int,
            "Number people exposed to > 1 Hematological HI": np.int,
            "Number people exposed to > 1 Immunological HI": np.int,
            "Number people exposed to > 1 Kidney HI": np.int,
            "Number people exposed to > 1 Liver HI": np.int,
            "Number people exposed to > 1 Neurological HI": np.int,
            "Number people exposed to > 1 Ocular HI": np.int,
            "Number people exposed to > 1 Reproductive HI": np.int,
            "Number people exposed to > 1 Respiratory HI": np.int,
            "Number people exposed to > 1 Skeletal HI": np.int,
            "Number people exposed to > 1 Spleen HI": np.int,
            "Number people exposed to > 1 Thyroid HI": np.int,
            "Number people exposed to > 1 Whole Body HI": np.int,
            "Number people exposed to >= 1 in 1,000 risk": np.int,
            "Number people exposed to >= 1 in 1,000,000 risk": np.int,
            "Number people exposed to >= 1 in 10,000 risk": np.int,
            "Number people exposed to >= 1 in 10,000,000 risk": np.int,
            "Number people exposed to >= 1 in 100,000 risk": np.int,
            "Octant or MIR": np.str,
            "Ocular HI": np.float64,
            "ocular_blk": np.str,
            "ocular_hi": np.float64,
            "ocular_hi_interptd": np.str,
            "ocular_rcpt_type": np.str,
            "Overlap": np.str,
            "Parameter": np.str,
            "Percentage": np.float64,
            "Pollutant": np.str,
            "pop_overlp": np.float64,
            "Population": np.int,
            "Rec_type": np.str,
            "Receptor type": np.str,
            "REL": np.float64,
            "Rel (mg/m3)": np.float64,
            "repro_blk": np.str,
            "repro_hi_interptd": np.str,
            "repro_rcpt_type": np.str,
            "Reproductive Facilities": np.int,
            "Reproductive HI": np.float64,
            "Reproductive Pop": np.int,
            "reproductive_hi": np.float64,
            "resp_blk": np.str,
            "resp_hi_interpltd": np.str,
            "resp_latitude": np.float64,
            "resp_longitude": np.float64,
            "resp_rcpt_type": np.str,
            "Respiratory Facilities": np.int,
            "Respiratory HI": np.float64,
            "Respiratory Pop": np.int,
            "respiratory_hi": np.float64,
            "RFc (mg/m3)": np.float64,
            "Ring number": np.int,
            "Risk": np.float64,
            "Risk Contribution": np.float64,
            "Risk level": np.str,
            "Risk Type": np.str,
            "Rural/Urban": np.str,
            "rural_urban": np.str,
            "Sector": np.int,
            "Site type": np.str,
            "skel_blk": np.str,
            "skel_hi_interptd": np.str,
            "skel_rcpt_type": np.str,
            "Skeletal HI": np.float64,
            "skeletal_hi": np.float64,
            "Source ID": np.str,
            'source_id': np.str,
            'Source_id': np.str,
            'SOURCE_ID': np.str,
            'SRCID': np.str, \
            "Spleen HI": np.float64,
            "spleen_blk": np.str,
            "spleen_hi": np.float64,
            "spleen_hi_interptd": np.str,
            "spleen_rcpt_type": np.str,
            "Src Cat": np.str,
            "Teel_0 (mg/m3)": np.float64,
            "Teel_1 (mg/m3)": np.float64,
            "Thyroid HI": np.float64,
            "thyroid_blk": np.str,
            "thyroid_hi": np.float64,
            "thyroid_hi_interptd": np.str,
            "thyroid_rcpt_type": np.str,
            "Total Inhalation As Cancer Risk": np.float64,
            "Total Inhalation Cancer Risk": np.float64,
            "Total Inhalation D/F Cancer Risk": np.float64,
            "Total Inhalation PAH Cancer Risk": np.float64,
            "URE 1/(ug/m3)": np.float64,
            "Utm easting": np.int,
            "UTM easting": np.int,
            "Utm northing": np.int,
            "UTM northing": np.int,
            "Utm_east": np.int,
            "Utm_north": np.int,
            "Value": np.float64,
            "Value rounded": np.float64,
            "Value scientific notation": np.float64,
            "Value_rnd": np.float64,
            "Value_sci": np.float64,
            "Warning": np.str,
            "Wet deposition (g/m2/yr)": np.float64,
            "Whole body HI": np.float64,
            "whole_blk": np.str,
            "whole_body_hi": np.float64,
            "whole_hi_interptd": np.str,
            "whole_rcpt_type": np.str,
            "X": np.int,
            "Y": np.int
        }

        filename = tk.filedialog.askopenfilename(filetypes = [("Excel or csv files","*.xls; *xlsx; *.csv*")])
        if filename.split(".")[-1].lower() in ["xlsx", "xls"]:
            df = pd.read_excel(filename, dtype=datatypes)#Added dtypes here
            ### Removing characters in column names that prevent pandastable calculations
            df.columns = df.columns.str.replace(' ', '_').str.replace('(', '') \
                .str.replace(')', '').str.replace('/','_').str.replace('%','pct') \
                .str.replace('>', 'gt').str.replace('>=', 'gte')
        else:
            df = pd.read_csv(filename, dtype=datatypes)
            ### Removing characters in column names that prevent pandastable calculations
            df.columns = df.columns.str.replace(' ', '_').str.replace('(', '') \
                .str.replace(')', '').str.replace('/','_').str.replace('%','pct') \
                .str.replace('>', 'gt').str.replace('>=', 'gte')

        curr_windo=tk.Toplevel()
        curr_windo.title(filename)
        curr_windo.geometry('900x600+40+20')
        pt = Table(curr_windo, dataframe = df, showtoolbar=True, showstatusbar=True)
        pt.autoResizeColumns()
        pt.colheadercolor='#448BB9'
        pt.floatprecision = 6
        pt.show()

    def maps_button(self):
        filename = tk.filedialog.askopenfilename(filetypes = [("html or kml files","*.html; *.kml; *.kmz")])
        webbrowser.open(filename)

    def browse(self):

        self.fullpath = tk.filedialog.askdirectory()
        #print(fullpath)
        self.mod_group_list.set(self.fullpath)

    def lift_nav(self):
        self.lower()
    #        self.b1.destroy()
    #
    #        self.b1 = tk.Button(self.buttonframe, text="Back", font=TEXT_FONT,
    #                       relief='solid', borderwidth=2, bg='lightgrey')
    #        self.b1.bind("<Enter>", partial(self.color_config, self.b1, "white"))
    #        self.b1.bind("<Leave>", partial(self.color_config, self.b1, "lightgrey"))
    ##        b2 = tk.Button(buttonframe, text="Page 2", command=p2.lift)
    ##        b3 = tk.Button(buttonframe, text="Page 3", command=p3.lift)
    ##
    #        self.b1.pack(side="bottom", fill="x", padx=5, pady=5)
    #       self.hem4 = hem4


    def color_config(self, widget, color, event):
        widget.configure(bg=color)


class MainView(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master=master, *args, **kwargs)
     
        home = self.master
        container = tk.Frame(self, bg="alice blue")
#        self.buttonframe.pack(side="right", fill="y", expand=False)
        container.pack(fill="both", expand=True)

        self.messageQueue = queue.Queue()
        self.callbackQueue = queue.Queue() 
        self.hem = Hem4(home, self.messageQueue, self.callbackQueue)
        #   start = Page1(self)
        self.nav = Page2(self)
        self.summary = Page1(self)
        self.analyze = Page3(self)

#        start.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.nav.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.hem.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.summary.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.analyze.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.summary.lower()
        self.hem.lower()
        self.analyze.lower()
        
     
        self.s=ttk.Style()
        print(self.s.theme_names())
        self.s.theme_use('clam')
        
         #create grid

        self.s1 = tk.Frame(container, width=750, height=100, bg="alice blue")
        self.s2 = tk.Frame(container, width=750, height=100, bg="alice blue")
        self.s3 = tk.Frame(container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s4 = tk.Frame(container, width=750, height=100, pady=5, padx=5, bg="alice blue")
        self.s5 = tk.Frame(container, width=750, height=100, pady=5, padx=5, bg="alice blue")

        self.s1.pack(fill="x")
        self.s2.pack(fill="x")
        self.s3.pack(fill="x")
        self.s4.pack(fill="x")
        self.s5.pack(fill="x")

        
        #title
        title = tk.Label(self.s1, text="What would you like to do?", font=TITLE_FONT, bg="alice blue")
        title.pack(padx=20, pady=50)
        
        #new facility run
        new_run = tk.Button(self.s2, text= "New Run", font=TEXT_FONT, 
                           relief='solid', borderwidth=2, bg='lightgrey', command=self.hem.lift)
        new_run.pack(padx=20, pady=50)
        new_run.bind("<Enter>", partial(self.color_config, new_run, "white"))
        new_run.bind("<Leave>", partial(self.color_config, new_run, "lightgrey"))
        
        #resume a facility run
        #first get all incomplete runs

#        incomplete_facs = os.listdir("save")
#        resume = tk.Label(self.s3, text= "Select a previously incompleted run", bg='alice blue', 
#                               font=TEXT_FONT).pack()
#
#        if len(incomplete_facs) > 0:
#            self.resume_var = tk.StringVar(self.s3)
#            self.resume_var.set(incomplete_facs[0])
#            self.resumeMenu = tk.OptionMenu(self.s3, self.resume_var, *incomplete_facs)
#            
#            self.resumeMenu.pack()
#
#        self.resume_button = tk.Button(self.s3, text="Resume a previous run (DISABLED)", font=TEXT_FONT, relief='solid', borderwidth=2, bg='lightgrey')
#        self.resume_button.pack()
        
        risk = tk.Button(self.s3, text= "Run Risk Summary Programs", font=TEXT_FONT, relief='solid', borderwidth=2, bg='lightgrey',
                             command=self.summary.lift)
        risk.pack(padx=20, pady=50)
        risk.bind("<Enter>", partial(self.color_config, risk, "white"))
        risk.bind("<Leave>", partial(self.color_config, risk, "lightgrey"))

        view = tk.Button(self.s4, text= "View and Analyze Outputs", font=TEXT_FONT, relief='solid', borderwidth=2, bg='lightgrey',
                         command=self.analyze.lift)
        view.pack(padx=20, pady=50)
        view.bind("<Enter>", partial(self.color_config, view, "white"))
        view.bind("<Leave>", partial(self.color_config, view, "lightgrey"))

        
#        #back button
#        back_button = tk.Button(self.s5, text="Back to Home", font=TEXT_FONT, relief='solid', borderwidth=2, bg='lightgrey'
#                            )
#        back_button.grid(row=1, sticky="W")
#        back_button.bind("<Enter>", partial(self.color_config, back_button, "white"))
#        back_button.bind("<Leave>", partial(self.color_config, back_button, "lightgrey"))
#  
        
        
        self.nav.lift()
        
    def color_config(self, widget, color, event):
       widget.configure(bg=color)
        

    def open_hem4(self):
        self.hem.reset_gui()
        
        
    def thread_resume(self):
        executor = ThreadPoolExecutor(max_workers=1)
#
        self.running = True
#        
        future = executor.submit(self.resume_run)
        future.add_done_callback(self.processing_finish)
        
        last = self.hem.tabControl.index('end')
        log = last - 2
        
        self.hem.tabControl.select(log)
        
        self.hem.lift()
      
        
        
    def resume_run(self):
        
        #get folder
        resume_folder = self.resume_var
        resume_loc = 'save/'+self.resume_var.get()
        
        resumemodel = resume_loc + '/model.pkl'
        #unpickle model
        modelfile = open(resumemodel,'rb')
        unpk_model = pickle.load(modelfile)
        modelfile.close()
        
        self.model = unpk_model
        
        #unpickle facids
        resumefac = resume_loc + "/remaining_facs.pkl"
        
        
        facfile = open(resumefac,'rb')
        
        try:
            unpk_facids = pickle.load(facfile)
            facfile.close()
        
        except:
            
            unpk_facids = self.model.faclist.dataframe['fac_id'].tolist()
            
        
        
        self.abort = threading.Event()
        
        self.aborted = False


        #replace facids
        self.model.facids = unpk_facids
        print('facids', unpk_facids)
        
        
        self.stop = tk.Button(self.hem.main, text="STOP", fg="red", font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                              command=self.quit_app)
        self.stop.grid(row=0, column=0, sticky="E", padx=5, pady=5)
        
        self.process()
        
       


# 

    def process(self):
        """
        Function creates thread for running HEM4 concurrently with tkinter GUI
        """
        
        
        # create Inputs folder
        inputspkgr = InputsPackager(self.model.rootoutput, self.model)
        inputspkgr.createInputs()

       
        Logger.logMessage("RUN GROUP: " + self.model.group_name)
        
        threadLocal = threading.local()

        threadLocal.abort = False


#        Logger.logMessage("Preparing Inputs for " + str(self.model.facids.count()) + " facilities\n")
        
        
       
        fac_list = []
        for i in self.model.facids:
            
            facid = i
            print(facid)
            fac_list.append(facid)
            num = 1

#        Logger.logMessage("The facility ids being modeled: , False)
        print("The facility ids being modeled: " + ", ".join(fac_list))

        success = False

        # Create output files with headers for any source-category outputs that will be appended
        # to facility by facility. These won't have any data for now.
        self.createSourceCategoryOutputs()
        
        self.skipped=[]
        for facid in fac_list:
            print(facid)
            if self.abort.is_set():
                Logger.logMessage("Aborting processing...")
                print("abort")
                return
            
            
            
            print("Running facility " + str(num) + " of " + str(len(fac_list)))
            
            success = False
                        
            try:
                runner = FacilityRunner(facid, self.model, self.abort)
                runner.setup()

            except BaseException as ex:

                self.exception = ex
                fullStackInfo=''.join(traceback.format_exception(
                    etype=type(ex), value=ex, tb=ex.__traceback__))

                message = "An error occurred while running a facility:\n" + fullStackInfo
                print(message)
                Logger.logMessage(message)
                
                
     
            ## if the try is successful this is where we would update the 
            # dataframes or cache the last processed facility so that when 
            # restart we know which faciltiy we want to start on
            # increment facility count
        
          
              
            try:
                self.model.aermod
                
            except:
                
                pass
            
            else:
                self.skipped.append(facid)
                self.model.aermod = None
            
            num += 1
            success = True
            

            #reset model options aftr facility
            self.model.model_optns = defaultdict()
            
#                try:  
#                    self.model.save.remove_folder()
#                except:
#                    pass
#                
        if self.abort.is_set():
            
            self.stop.destroy()
            
            Logger.logMessage('HEM4 RUN GROUP: ' + str(self.model.group_name) + ' canceled.')    
        
        elif len(self.skipped) == 0:
            
            self.model.save.remove_folder()
            self.stop.destroy()
            
            Logger.logMessage("HEM4 Modeling Completed. Finished modeling all" +
                          " facilities. Check the log tab for error messages."+
                          " Modeling results are located in the Output"+
                          " subfolder of the HEM4 folder.")

        else:

            self.model.save.remove_folder()
            self.stop.destroy()
            
            Logger.logMessage("HEM4 Modeling not completed for " + ", ".join(self.skipped))
         #remove save folder after a completed run
        

     #remove save folder after a completed run

    
    

            return success

    def processing_finish(self, future):
        """
        Callback that gets run in the same thread as the processor, after the target method
        has finished. It's purpose is to update the shared callback queue so that the main
        thread can update the GUI (which cannot be done in this thread!)
        :param future:
        :return: None
        """
        self.callbackQueue.put(self.finish_run)

    def finish_run(self):
        """
        Return Hem4 running state to False, and either reset or quit the GUI, depending on
        whether or not the processing finished naturally or was aborted.
        :return: None
        """
        self.running = False

#        if self.aborted:
#            self.reset_gui()
#        else:
#            self.reset_gui()
    
    def abortProcessing(self):
        self.abort.set()
        
    def quit_app(self):
        """
        
        Function handles quiting HEM4 by closing the window containing
        the GUI and exiting all background processes & threads
        """
        if self.running:
            override = messagebox.askokcancel("Confirm HEM4 Resume Quit", "Are you "+
                                              "sure? HEM4 is currently running. Clicking 'OK' will stop HEM4.")

            if override:
                # Abort the thread and wait for it to stop...once it has
                # completed, it will signal this class to kill the GUI
                Logger.logMessage("Stopping HEM4...")
                self.abortProcessing()
                self.aborted = True


        else:
            # If we're not running, the only thing to do is reset the GUI...
            self.reset_gui()
            Logger.logMessage("HEM4 stopped")
    
    def check_processing(self):
        """
        Check the callback queue to see if the processing thread has indicated that
        it's finished running. If an entry is found, it's the method to run that
        instructs this class how to reset/kill the GUI. If not, schedule another
        check soon.
        :return: None
        """
        try:
            callback = self.callbackQueue.get(block=False)
        except queue.Empty: #raised when queue is empty
            self.after(500, self.check_processing)
            return

        print("About to call callback...")
        callback()

    def after_callback(self):
        """
        Function listens on thread RUnning HEM4 for error and completion messages
        logged via queue method
        """
        try:
            message = self.messageQueue.get(block=False)
        except queue.Empty:
            # let's try again later
            self.after(25, self.after_callback)
            return

        print('after_callback got', message)
        if message is not None:
            self.hem.scr.configure(state='normal')
            self.hem.scr.insert(tk.INSERT, message)
            self.hem.scr.insert(tk.INSERT, "\n")
            self.hem.scr.configure(state='disabled')
            self.after(25, self.after_callback)
            
            
    def createSourceCategoryOutputs(self):
        
        # Create Facility Max Risk and HI file
        fac_max_risk = FacilityMaxRiskandHI(self.model.rootoutput, None, self.model, None, None)
        fac_max_risk.write()
        
        # Create Facility Cancer Risk Exposure file
        fac_canexp = FacilityCancerRiskExp(self.model.rootoutput, None, self.model, None)
        fac_canexp.write()
        
        # Create Facility TOSHI Exposure file
        fac_hiexp = FacilityTOSHIExp(self.model.rootoutput, None, self.model, None)
        fac_hiexp.write()




    @staticmethod
    def center_main():
        # Gets the requested values of the height and width.
        windowWidth = root.winfo_reqwidth()
        windowHeight = root.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        positionRight = int(root.winfo_screenwidth()/2 - windowWidth)
        positionDown = int(root.winfo_screenheight()/2 - (windowHeight/2 + 100))

        # Positions the window in the center of the page.
        root.geometry("+{}+{}".format(positionRight, positionDown))

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap('images/HEM4.ico')
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_minsize(1000,750)

    main.after(20, MainView.center_main)
    root.mainloop()
