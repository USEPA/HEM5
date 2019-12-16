# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 23:29:19 2019

@author: David Lindsey
"""

import tkinter as tk
import webbrowser
import tkinter.ttk as ttk
from functools import partial
from com.sca.hem4.GuiThreaded import Hem4
import queue

import os

from PIL import ImageTk, Image


TITLE_FONT= ("Verdana", 18)
TEXT_FONT = ("Verdana", 14)

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
        
        container = tk.Frame(self, bg="palegreen3")
#        self.buttonframe.pack(side="right", fill="y", expand=False)
        container.pack(side="top", fill="both", expand=True)
        
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
        self.s5.pack(fill="y")
        
        #title
        title = tk.Label(self.s1, text="Risk Summary", font=TITLE_FONT, bg="palegreen3")
        title.pack(pady=10, side="top")
        
        #instructions
        instructions = tk.Label(self.s1, text="Select one or more risk summary programs", font=TEXT_FONT, bg="palegreen3")
        instructions.pack()
        
         #modeling group label
        group_label = tk.Label(self.s2, font=TEXT_FONT, bg="palegreen3", 
                             text="Please select a modeling group:")
        group_label.pack(pady=20, padx=5, side="left")
        
        #file browse button
        self.mod_group = tk.Button(self.s3, command = lambda: self.browse, font=TEXT_FONT, relief='solid', borderwidth=2)
        self.mod_group["text"] = "Browse"
        self.mod_group.pack(side='left', padx=5, pady=10)
        
        #output directory path
        self.mod_group_list = tk.StringVar(self.s3)
        self.group_list_man = ttk.Entry(self.s3)
        self.group_list_man["width"] = 75
        self.group_list_man["textvariable"]= self.mod_group_list
        self.group_list_man.pack(padx=20, side="left", pady=10)
       
        
        var_m = tk.IntVar()
        max_risk = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="palegreen3", text="Max Risk Summary", variable=var_m)
        max_risk.pack(fill="x")
        
        var_c = tk.IntVar()
        cancer_driver = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="palegreen3", text="Cancer Drivers Summary", variable=var_c)
        cancer_driver.pack(fill="x")
        
        var_h = tk.IntVar()
        hazard = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="palegreen3", text=" Hazard Index Drivers Summary", variable=var_h)
        hazard.pack(fill="x")
        
        var_hi = tk.IntVar()
        hist = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="palegreen3", text="Histogram", variable=var_hi)
        hist.pack(fill="x")
        
        var_hh = tk.IntVar()
        hh = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="palegreen3", text="HI Histogram", variable=var_hh)
        hh.pack(fill="x")
        
        var_i = tk.IntVar()
        inc = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="palegreen3", text="Incidence Drivers Summary", variable=var_i)
        inc.pack(fill="x")
        
        var_a = tk.IntVar()
        ai = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="palegreen3", text="Acute Impacts Summary", variable=var_a)
        ai.pack(fill="x")
        
        var_s = tk.IntVar()
        s = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="palegreen3", text="Source Type Risk Histogram", variable=var_s)
        s.pack(fill="x")
        
        var_p = tk.IntVar()
        mp = tk.Checkbutton(self.s4, font=TEXT_FONT, bg="palegreen3", text=" Multi Pathway", variable=var_p)
        mp.pack(fill="x")
        
     
        #back button
        back_button = tk.Button(self.s5, text="Back", font=TEXT_FONT, relief='solid', borderwidth=2,
                            command=self.lower)
        back_button.pack(side="left", padx=5, pady=10)

    def browse(self):
        
        fullpath = tk.filedialog.askopenfilename()
        
        self.mod_group_list = fullpath
        
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