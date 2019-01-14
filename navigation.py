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

TITLE_FONT= ("Verdana", 12)
TEXT_FONT = ("Verdana", 10)



class Navigation(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
         #create grid
        self.s1 = tk.Frame(self, width=500, height=50)
        self.s2 = tk.Frame(self, width=500, height=100)
        self.s3 = tk.Frame(self, width=500, height=100, pady=10, padx=10)
        self.s4 = tk.Frame(self, width=500, height=100, pady=10, padx=10)
        self.s5 = tk.Frame(self, width=500, height=100, pady=10, padx=10)
        

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
        new_run = tk.Button(self.s2, text= "Run a new Facility", font=TEXT_FONT,
                            command=lambda:controller.show_frame(hem4.Hem4))
        new_run.grid(row=1)

        #summarize risk
        #fist get all facilities in output 
        completed_facs = os.listdir("output")
        sum_var = tk.StringVar(self.s3).set(completed_facs[1])
        popupMenu = tk.OptionMenu(self.s3, sum_var, *completed_facs)
        summary= tk.Label(self.s3, text="Run Risk Summary on completed facility").grid(row = 1)
        popupMenu.grid(row = 2)
        
        #back button
        back_button = tk.Button(self.s5, text="Back to Home", font=TEXT_FONT,
                            command=lambda: controller.show_frame(startpage.StartPage))
        back_button.grid(row=1, sticky="W")

#  