# -*- coding: utf-8 -*-
"""

@author: David Lindsey
"""
import tkinter as tk
import os

#get navigation page
from navigation import Navigation

TITLE_FONT= ("Verdana", 20)
TEXT_FONT = ("Verdana", 15)



class Summary(tk.Frame):

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
        title = tk.Label(self.s1, text="Risk Summary", font=TITLE_FONT)
        title.grid(row=1)
        
        
        #back button
        back_button = tk.Button(self.s5, text="Back", font=TEXT_FONT,
                            command=lambda: controller.show_frame(navigation.Navigation))
        back_button.grid(row=1, sticky="W")

#  