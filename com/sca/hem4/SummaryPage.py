# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 12:55:29 2020

@author: David Lindsey
"""

import tkinter as tk
import webbrowser
import tkinter.ttk as ttk
from functools import partial
from com.sca.hem4.GuiThreaded import Hem4
import queue

import os
import glob
import importlib 

from PIL import ImageTk, Image

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

class SummaryPage():
    
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, master=nav, *args, **kwargs)
        
        
        self.noteStyler = ttk.Style()
        self.noteStyler.configure("TNotebook", background="palegreen3", borderwidth=0)
        self.noteStyler.configure("TNotebook.Tab", background="palegreen3", borderwidth=0)
        self.noteStyler.configure("TFrame", background="palegreen3", borderwidth=0)

        
        # Tab Control introduced here --------------------------------------
        self.tabControl = ttk.Notebook(self, style='TNotebook')     # Create Tab Control
        
        self.container = tk.Frame(self, bg="palegreen3")
#        self.buttonframe.pack(side="right", fill="y", expand=False)
        
        self.s=ttk.Style()
        print(self.s.theme_names())
        self.s.theme_use('clam')
        
        
        self.tabControl.add(self.container, text='HEM4')      # Add the tab

        self.log2 = tk.Frame(self.tabControl, bg='palegreen3')            # Add a second tab
        self.tabControl.add(self.log2, text='Log')      # Make second tab visible

        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible

         #create grid
        self.s1 = tk.Frame(self.container, width=750, height=100, bg="palegreen3")
        self.s2 = tk.Frame(self.container, width=750, height=100, bg="palegreen3")
        self.s3 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s4 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s5 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s6 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s7 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s8 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s9 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s10 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s11 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s12 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
          
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



        self.container.grid_rowconfigure(8, weight=4)
        self.container.grid_columnconfigure(2, weight=1)

        
        #title
        title = tk.Label(self.s1, text="Risk Summary", font=TITLE_FONT, bg="palegreen3")
        title.grid(row=1, pady=10)
        
        #instructions
        instructions = tk.Label(self.s1, text="Select one or more risk summary programs", font=TEXT_FONT, bg="palegreen3")
        instructions.grid(row=2)
        
         #modeling group label
        group_label = tk.Label(self.s2, font=TEXT_FONT, bg="palegreen3", 
                             text="Please identify the location of the HEM4 results to be summarized:")
        group_label.grid(row=1, pady=5, padx=5)
        
        #file browse button
        self.mod_group = tk.Button(self.s2, command = self.browse, font=TEXT_FONT, relief='solid', borderwidth=2)
        self.mod_group["text"] = "Browse"
        self.mod_group.grid(row=2, column=0, sticky="W")
        
        #output directory path
        self.mod_group_list = tk.StringVar(self.s3)
        self.group_list_man = ttk.Entry(self.s3)
        self.group_list_man["width"] = 250
        self.group_list_man["textvariable"]= self.mod_group_list
        self.group_list_man.grid(row=2, column=0, sticky="E")
       
        
        
        
        self.var_m = tk.IntVar()
        max_risk = tk.Checkbutton(self.s3, font=TEXT_FONT, bg="palegreen3", text="Max Risk Summary", variable=self.var_m)
        max_risk.grid(row=1, padx=10, sticky="W")
        
        
        self.var_c = tk.IntVar()
        cancer_driver = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="palegreen3", text="Cancer Drivers Summary", variable=self.var_c)
        cancer_driver.grid(row=1, padx=10, sticky="W")
        
        self.var_h = tk.IntVar()
        hazard = tk.Checkbutton(self.s5, font=TEXT_FONT, bg="palegreen3", text=" Hazard Index Drivers Summary", variable=self.var_h)
        hazard.grid(row=1, padx=10, sticky="W")
        
        self.var_hi = tk.IntVar()
        hist = tk.Checkbutton(self.s6, font=TEXT_FONT, bg="palegreen3", text="Risk Histogram", variable=self.var_hi)
        hist.grid(row=1, padx=10, sticky="W")
        
        self.var_hh = tk.IntVar()
        hh = tk.Checkbutton(self.s7, font=TEXT_FONT, bg="palegreen3", text="HI Histogram", variable=self.var_hh)
        hh.grid(row=1, padx=10, sticky="W")
        
        self.var_i = tk.IntVar()
        inc = tk.Checkbutton(self.s8, font=TEXT_FONT, bg="palegreen3", text="Incidence Drivers Summary", variable=self.var_i)
        inc.grid(row=1, padx=10, sticky="W")
        
        self.var_a = tk.IntVar()
        ai = tk.Checkbutton(self.s9, font=TEXT_FONT, bg="palegreen3", text="Acute Impacts Summary", variable=self.var_a)
        ai.grid(row=1, padx=10, sticky="W")
        
        self.var_p = tk.IntVar()
        mp = tk.Checkbutton(self.s10, font=TEXT_FONT, bg="palegreen3", text=" Multi Pathway", variable=self.var_p)
        mp.grid(row=1, padx=10, sticky="W")
        
        self.var_s = tk.IntVar()
        s = tk.Checkbutton(self.s11, font=TEXT_FONT, bg="palegreen3", text="Source Type Risk Histogram", variable=self.var_s)
        s.grid(row=1, padx=10, sticky="W")
        
        pos = tk.Label(self.s4, font=SUB_FONT, bg="palegreen3", text="Enter the position in the source ID where the\n source ID type begins.The default is 1.")
       
        
        self.pos_num = ttk.Entry(self.s4)
        self.pos_num["width"] = 5
        
        chars = tk.Label(self.s4, font=SUB_FONT, bg="palegreen3", text="Enter the number of characters of the sourcetype ID")
        
        self.chars_num = ttk.Entry(self.s4)
        self.chars_num["width"] = 5
        
   
        
        
        
        #back button
        back_button = tk.Button(self.s12, text="Back", font=TEXT_FONT, relief='solid', borderwidth=2,
                            command=self.lower)
        back_button.grid(row=0, column=0, sticky="W", padx=5, pady=10)
        
        run_button = tk.Button(self.s12, text="Run Reports", font=TEXT_FONT, relief='solid', borderwidth=2,
                            command= self.createReports)
        run_button.grid(row=0, column=0, sticky="E", padx=5, pady=10)
        
    def browse(self):
        
        self.fullpath = tk.filedialog.askdirectory()
        #print(fullpath)
        self.mod_group_list.set(self.fullpath)
        

        
    def createReports(self,  arguments=None):
        
        # Figure out which facilities will be included in the report
        files = os.listdir(self.fullpath)
        rootpath = self.fullpath+'/'
        faclist = [ item for item in files if os.path.isdir(os.path.join(rootpath, item)) 
                    and 'inputs' not in item.lower() and 'acute maps' not in item.lower() ]
                
        #get reports
        reportNames = []
        if self.var_m.get() == 1:
            reportNames.append('MaxRisk')
        if self.var_c.get() == 1:
            reportNames.append('CancerDrivers')
        if self.var_h.get() == 1:
            reportNames.append('HazardIndexDrivers')
        if self.var_hi.get() == 1:
            reportNames.append('Histogram')
        if self.var_hh.get() == 1:
            reportNames.append('HI_Histogram')
        if self.var_i.get() == 1:
            reportNames.append('IncidenceDrivers')
        #if self.var_a.get() == 1:
        #    reportNames.append('AcuteImpacts')
        if self.var_s.get() == 1:
            reportNames.append('SourceTypeRiskHistogram')
            #pass position number and character number
            self.pos_num
            self.chars_num
            
            
        if self.var_p.get() == 1:
            reportNames.append('MultiPathway')
        
        
        print("Running report on facilities: " + ', '.join(faclist))

        summaryMgr = SummaryManager(self.fullpath, faclist)
        
        #loop through for each report selected
        for reportName in reportNames:
            summaryMgr.createReport(self.fullpath, reportName)

    
    def color_config(self, widget, color, event):
         widget.configure(bg=color)