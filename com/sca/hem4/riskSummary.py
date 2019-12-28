# -*- coding: utf-8 -*-
"""

@author: David Lindsey
"""
import tkinter as tk
from tkinter.filedialog import askopenfilename
import os
import tkinter.ttk as ttk

#get navigation page
#import navigation

TITLE_FONT= ("Verdana", 18)
TEXT_FONT = ("Verdana", 14)



class Summary(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        self.s = ttk.Style()
        print(self.s.theme_names())
        self.s.theme_use('clam')
        
         #create grid
        self.s1 = tk.Frame(self, width=750, height=100, bg="palegreen3")
        self.s2 = tk.Frame(self, width=750, height=100, bg="palegreen3")
        self.s3 = tk.Frame(self, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s4 = tk.Frame(self, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        self.s5 = tk.Frame(self, width=750, height=100, pady=5, padx=5, bg="palegreen3")
        

        self.s1.grid(row=0)
        self.s2.grid(row=1, column=0, sticky="nsew")
        self.s3.grid(row=2, column=0, sticky="nsew")
        self.s4.grid(row=3, column=0, sticky="nsew")
        self.s5.grid(row=4, column=0, sticky="nsew")

        for frame in [self.s1, self.s2, self.s3, self.s4, self.s5]:
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            frame.grid_propagate(0)
        
        #title
        title = tk.Label(self.s1, text="Risk Summary", font=TITLE_FONT, bg="steelblue")
        title.grid(row=1)
        
        #instructions
        instructions = tk.Label(self.s1, text="Select one or more risk summary programs", font=TEXT_FONT, bg="steelblue")
        instructions.grid(row=2)
        
         #modeling group label
        group_label = tk.Label(self.s2, font=TEXT_FONT, bg="steelblue", 
                             text="Please select a modeling group:")
        group_label.grid(row=1, sticky="W")
        
        #file browse button
        self.mod_group = tk.Button(self.s2, command = lambda: self.browse(), relief='solid', borderwidth=1,)
        self.mod_group["text"] = "Browse"
        self.mod_group.grid(row=2, sticky="W", padx=10)
        
        #output directory path
        self.mod_group_list = tk.StringVar(self.s2)
        self.group_list_man = ttk.Entry(self.s2)
        self.group_list_man["width"] = 100
        self.group_list_man["textvariable"]= self.mod_group_list
        self.group_list_man.grid(row=2, sticky='W', padx=95)
       
        
        
        #back button
        back_button = tk.Button(self.s5, text="Back", font=TEXT_FONT, relief='solid', borderwidth=2,
                            command=lambda: controller.show_frame(navigation.Navigation))
        back_button.grid(row=1, sticky="W")

    def browse(self):
        
        fullpath = filedialog.askdirectory()
        
        self.mod_group_list = fullpath
