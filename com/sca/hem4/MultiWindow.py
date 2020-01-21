# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 23:29:19 2019

@author: David Lindsey
"""

import tkinter as tk
import webbrowser
import tkinter.ttk as ttk
from tkinter import scrolledtext
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

class Page1(Page):
    
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
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
        
        
        self.tabControl.add(self.container, text='Summaries')      # Add the tab

        self.log2 = tk.Frame(self.tabControl, bg='palegreen3')            # Add a second tab
        self.tabControl.add(self.log2, text='Log')      # Make second tab visible
    
        
        # Adding a Textbox Entry widget
#        scrolW  = 65; scrolH  =  25
        self.scr = scrolledtext.ScrolledText(self.log2, wrap=tk.WORD, width=1000, height=1000, font=TEXT_FONT)
        self.scr.pack()

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
        self.s13 = tk.Frame(self.container, width=750, height=100, pady=5, padx=5, bg="palegreen3")

          
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
        title = tk.Label(self.s1, text="Risk Summary", font=TITLE_FONT, bg="palegreen3")

        title.grid(row = 1)
        
        #instructions
        instructions = tk.Label(self.s1, text="Select one or more risk summary programs", font=TEXT_FONT, bg="palegreen3")
        instructions.grid_columnconfigure(1, weight=1)
        instructions.grid(row=2)
        
         #modeling group label
        group_label = tk.Label(self.s1, font=TEXT_FONT, bg="palegreen3", 
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
        s = tk.Checkbutton(self.s11, font=TEXT_FONT, bg="palegreen3", text="Source Type Risk Histogram", variable=self.var_s, command=self.set_sourcetype)
        s.grid(row=1, padx=10, sticky="W")
        
        
           
        
        #back button
        back_button = tk.Button(self.s13, text="Back", font=TEXT_FONT, relief='solid', borderwidth=2,
                            command=self.lower)
        back_button.grid(row=0, column=2, sticky="W", padx=5, pady=10)
        
        run_button = tk.Button(self.s13, text="Run Reports", font=TEXT_FONT, relief='solid', borderwidth=2,
                            command= self.createReports)
        run_button.grid(row=0, column=1, sticky="E", padx=5, pady=10)
        
    def browse(self):
        
        self.fullpath = tk.filedialog.askdirectory()
        #print(fullpath)
        self.mod_group_list.set(self.fullpath)
        
    def set_sourcetype(self):

        if self.var_s.get() == 1:
        
            self.pos = tk.Label(self.s12, font=SUB_FONT, bg="palegreen3", text="Enter the position in the source ID where the\n source ID type begins.The default is 1.")
            self.pos.grid(row=1, padx=10, sticky="W")
            
            self.pos_num = ttk.Entry(self.s12)
            self.pos_num["width"] = 5
            self.pos_num.grid(row=1, column=2, padx=10, sticky="W")
        
            self.chars = tk.Label(self.s12, font=SUB_FONT, bg="palegreen3", text="Enter the number of characters \nof the sourcetype ID")
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
        
    def createReports(self,  arguments=None):
        
        # Figure out which facilities will be included in the report
        files = os.listdir(self.fullpath)
        rootpath = self.fullpath+'/'
        faclist = [ item for item in files if os.path.isdir(os.path.join(rootpath, item)) 
                    and 'inputs' not in item.lower() ]
                
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
            reportNameArgs['HI Histogram'] = None
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
        
        
        running_message = "Running report on facilities: " + ', '.join(faclist)
        
        self.scr.configure(state='normal')
        self.scr.insert(tk.INSERT, running_message)
        self.scr.insert(tk.INSERT, "\n")
        self.scr.configure(state='disabled')

        summaryMgr = SummaryManager(self.fullpath, faclist)
        
        #loop through for each report selected
        for reportName in reportNames:
            report_message = "Creating " + reportName + " report."
            
            self.scr.configure(state='normal')
            self.scr.insert(tk.INSERT, report_message)
            self.scr.insert(tk.INSERT, "\n")
            self.scr.configure(state='disabled')
            
            args = reportNameArgs[reportName]
            summaryMgr.createReport(self.fullpath, reportName, args)
            
            report_complete = reportName +  " complete."
            self.scr.configure(state='normal')
            self.scr.insert(tk.INSERT, report_complete)
            self.scr.insert(tk.INSERT, "\n")
            self.scr.configure(state='disabled')
            
        self.scr.configure(state='normal')
        self.scr.insert(tk.INSERT, "Summary Reports Complete.")
        self.scr.insert(tk.INSERT, "\n")
        self.scr.configure(state='disabled')
        
        
    
    def color_config(self, widget, color, event):
         widget.configure(bg=color)

class Page2(Page):
    def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
   
       container = tk.Frame(self, bg="palegreen3")
#        self.buttonframe.pack(side="right", fill="y", expand=False)
       container.pack(side="top", fill="both", expand=True)
       
       self.s1 = tk.Frame(container, width=600, height=50, bg="palegreen3")
       self.s2 = tk.Frame(container, width=600, height=50, bg="palegreen3")
       self.s3 = tk.Frame(container, width=600, height=50, pady=5, padx=5, bg="palegreen3")
       self.s4 = tk.Frame(container, width=600, height=50, pady=5, padx=5, bg="palegreen3")
       self.s5 = tk.Frame(container, width=600, height=50, pady=5, padx=5, bg="palegreen3")
          
       self.s1.pack(fill="x")
       self.s2.pack(fill="x")
       self.s3.pack(fill="x")
       self.s4.pack(fill="x")
       self.s5.pack(fill="x")
        
        #title in first grid space 
       title1 = tk.Label(self.s1, text="HEM4", font=TITLE_FONT, bg="palegreen3")
       title1.pack(side="top", pady=20)
        
       title2 = tk.Label(self.s1, text="Human Exposure Model\n Version 4-Open Source ", font=TEXT_FONT, bg="palegreen3")
       title2.pack()
        

       #some information
       prepared_for = tk.Label(self.s2, text="Prepared for: \nAir Toxics" +
                            " Assessment Group \nU.S. EPA \nResearch Triangle Park, NC 27711", 
                             font=TEXT_FONT, bg="palegreen3")
       prepared_for.pack(padx=45, pady=30, side="left")
       
       
       image1 = ImageTk.PhotoImage(Image.open('images\smokestack.jpg'))
       ione = tk.Label(self.s3, image=image1)
       ione.image = image1 # keep a reference!
       ione.pack(padx=50, side="left")
       
                
       prepared_by = tk.Label(self.s2, text="Prepared by: \nSC&A Incorporated\n" +
                            "1414 Raleigh Rd, Suite 450\nChapel Hill, NC 27517", 
                             font=TEXT_FONT, bg="palegreen3") 
       prepared_by.pack(padx=150, pady=30)
       
       
#       image2 = ImageTk.PhotoImage(Image.open('images\residential.jpg'))s
#       itwo = tk.Label(self.s3, image=image2)
#       itwo.image = image2 # keep a reference!
#       itwo.pack(padx=20, side="right")
       

        
        ## hyperlink 
       link_to_site = tk.Label(self.s3, text="EPA HEM4 Webpage (link)", 
                               font=TEXT_FONT, bg="palegreen3")
       link_to_site.pack(pady=30, padx=100)
       link_to_site.bind('<Button-1>', hyperlink1)
        
       link_to_userguide = tk.Label(self.s3, text="HEM4 User's Guide (link)", 
                                      font=TEXT_FONT, bg="palegreen3")
       link_to_userguide.pack(pady=10, padx=100)
       link_to_userguide.bind("<Button-1>", hyperlink2)
        
       self.b1 = tk.Button(self.s3, text="Start Menu", font=TEXT_FONT, 
                       relief='solid', borderwidth=2, bg='lightgrey', command=self.lift_nav)
       self.b1.bind("<Enter>", partial(self.color_config, self.b1, "white"))
       self.b1.bind("<Leave>", partial(self.color_config, self.b1, "lightgrey"))
#
       self.b1.pack(pady=20)

       #start.show()

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
        container = tk.Frame(self, bg="palegreen3")
#        self.buttonframe.pack(side="right", fill="y", expand=False)
        container.pack(fill="both", expand=True)

        messageQueue = queue.Queue()
        callbackQueue = queue.Queue() 
        self.hem = Hem4(home, messageQueue, callbackQueue)
        #   start = Page1(self)
        self.nav = Page2(self)
#        hem = Page3(self)
        self.summary = Page1(self)
       
#        start.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.nav.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.hem.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.summary.place(in_=container, x=0, y=0, relwidth=1, relheight=1) 
        self.summary.lower()
        self.hem.lower()
        
     
        self.s=ttk.Style()
        print(self.s.theme_names())
        self.s.theme_use('clam')
        
         #create grid

        self.s1 = tk.Frame(container, width=750, height=100, bg="palegreen3")
        self.s2 = tk.Frame(container, width=750, height=100, bg="palegreen3")
        self.s3 = tk.Frame(container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s4 = tk.Frame(container, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s5 = tk.Frame(container, width=750, height=100, pady=5, padx=5, bg="palegreen3")

        self.s1.pack(fill="x")
        self.s2.pack(fill="x")
        self.s3.pack(fill="x")
        self.s4.pack(fill="x")
        self.s5.pack(fill="x")

        
        #title
        title = tk.Label(self.s1, text="What would you like to do?", font=TITLE_FONT, bg="palegreen3")
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
        resume = tk.Label(self.s3, text= "Resume Previous Run (DISABLED)", bg='palegreen3', 
                               font=TEXT_FONT).pack()
#
#        if len(incomplete_facs) > 1:
#            resume_var = tk.StringVar(self.s3).set(incomplete_facs[1])
#            resumeMenu = tk.OptionMenu(self.s3, resume_var, *incomplete_facs)
#            
#            resumeMenu.grid(row=2)
#        
#        #summarize risk
#        completed_facs = os.listdir("output")
#        ignore = ['HAP_ignored.log', 'hem4.log', 'SC_max_risk_and_hi.xlsx']
#        folders = [x for x in completed_facs if x not in ignore]
#        
#        sum_var = tk.StringVar(self.s4).set(folders[1])
#        popupMenu = tk.OptionMenu(self.s4, sum_var, *folders)
#        popupMenu.grid(row = 2)
        
        risk = tk.Button(self.s4, text= "Run Risk Summary Programs", font=TEXT_FONT, relief='solid', borderwidth=2, bg='lightgrey',
                             command=self.summary.lift)
        risk.pack(padx=20, pady=50)
        risk.bind("<Enter>", partial(self.color_config, risk, "white"))
        risk.bind("<Leave>", partial(self.color_config, risk, "lightgrey"))

        view = tk.Button(self.s5, text= "View and Analyze Outputs (Disabled) ", font=TEXT_FONT, relief='solid', borderwidth=2, bg='lightgrey')
        view.pack(padx=20, pady=50)
        view.bind("<Enter>", partial(self.color_config, risk, "white"))
        view.bind("<Leave>", partial(self.color_config, risk, "lightgrey"))

        
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

if __name__ == "__main__":
    root = tk.Tk()
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_minsize(1000,750)
    root.mainloop()