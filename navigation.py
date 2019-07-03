# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 11:56:44 2018

@author: David Lindsey
"""
import tkinter as tk
import os

#get other pages for navigation
import startpage
import hem4Window as hem4
import riskSummary

TITLE_FONT= ("Verdana", 20)
TEXT_FONT = ("Verdana", 15)



class Navigation(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
         #create grid
        self.s1 = tk.Frame(self, width=1000, height=150)
        self.s2 = tk.Frame(self, width=1000, height=150)
        self.s3 = tk.Frame(self, width=1000, height=150, pady=10, padx=10)
        self.s4 = tk.Frame(self, width=1000, height=150, pady=10, padx=10)
        self.s5 = tk.Frame(self, width=1000, height=150, pady=10, padx=10)
        

        self.s1.grid(row=0)
        self.s2.grid(row=1, column=0, sticky="nsew")
        self.s3.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.s4.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.s5.grid(row=4, column=0, columnspan=2, sticky="nsew")

        for frame in [self.s1, self.s2, self.s3, self.s4, self.s5]:
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            frame.grid_propagate(0)
        
        #title
        title = tk.Label(self.s1, text="What would you like to do?", font=TITLE_FONT)
        title.grid(row=1)
        
        #new facility run
        new_run = tk.Button(self.s2, text= "Run a new facility", font=TEXT_FONT,
                            command=lambda:controller.show_frame(hem4.Hem4))
        new_run.grid(row=1)
        
        #resume a facility run
        #first get all incomplete runs
        incomplete_facs = os.listdir("save")
        resume = tk.Label(self.s3, text= "Resume a previous facility run", 
                               font=TEXT_FONT).grid(row=1)
        
        if len(incomplete_facs) > 1:
            resume_var = tk.StringVar(self.s3).set(incomplete_facs[1])
            resumeMenu = tk.OptionMenu(self.s3, resume_var, *incomplete_facs)
            
            resumeMenu.grid(row=2)
        
#        #summarize risk
#        completed_facs = os.listdir("output")
#        ignore = ['HAP_ignored.log', 'hem4.log', 'SC_max_risk_and_hi.xlsx']
#        folders = [x for x in completed_facs if x not in ignore]
#        
#        sum_var = tk.StringVar(self.s4).set(folders[1])
#        popupMenu = tk.OptionMenu(self.s4, sum_var, *folders)
#        popupMenu.grid(row = 2)
        
         #new facility run
        risk = tk.Button(self.s4, text= "Run risk summary", font=TEXT_FONT,
                            command=lambda:controller.show_frame(riskSummary.Summary))
        risk.grid(row=1)
        
        #back button
        back_button = tk.Button(self.s5, text="Back to Home", font=TEXT_FONT,
                            command=lambda: controller.show_frame(startpage.StartPage))
        back_button.grid(row=1, sticky="W")

#  