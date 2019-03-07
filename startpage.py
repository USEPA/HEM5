# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 11:53:53 2018

@author: David Lindsey
"""
import tkinter as tk
import webbrowser

import navigation


TITLE_FONT= ("Verdana", 20)
TEXT_FONT = ("Verdana", 16)

def hyperlink1(event):
    webbrowser.open_new(r"https://www.epa.gov/fera/risk-assessment-and-"+
                        "modeling-human-exposure-model-hem")

def hyperlink2(event):
    webbrowser.open_new(r"https://www.epa.gov/fera/human-exposure-model-hem-3"+
                        "-users-guides")

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        
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
        
        #title in first grid space 
        title = tk.Label(self.s1, text="Human Exposure Model 4", font=TITLE_FONT)
        title.grid(row=1)
        
        #some information
        some_info = tk.Label(self.s2, text="Some information about HEM4", 
                             font=TEXT_FONT)
        some_info.grid(row=1)
                
        ## hyperlink 
        link_to_site = tk.Label(self.s3, text="HEM4 site link", fg="blue", 
                                font=TEXT_FONT)
        link_to_site.grid(row=1)
        link_to_site.bind('<Button-1>', hyperlink1)
        
        link_to_userguide = tk.Label(self.s4, text="Userguide hosted link", 
                                     fg='blue', font=TEXT_FONT)
        link_to_userguide.grid(row=1)
        link_to_userguide.bind("<Button-1>", hyperlink2)
        
        #next button
        button = tk.Button(self.s5, text="Next", font=TEXT_FONT,
                            command=lambda: controller.show_frame(navigation.Navigation))
        button.grid(row=1, sticky="E")

 