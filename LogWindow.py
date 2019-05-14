# -*- coding: utf-8 -*-
"""
Created on Wed May  8 20:21:57 2019

@author: David Lindsey
"""


import tkinter as tk
from tkinter import scrolledtext
import logging

class LogWindow(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        #setup goes here
        self.log = tk.Frame(self, width=1000, height=150)
        self.log.grid(row=0, column=0)
        scrolW  = 65; scrolH  =  25
        self.scr = scrolledtext.ScrolledText(self.log, width=scrolW, 
                                                    height=scrolH, wrap=tk.WORD)
        self.scr.grid(column=0, row=0, sticky='WE', columnspan=3)
        

class MyHandlerText(logging.StreamHandler):
    def __init__(self, textctrl):
        logging.StreamHandler.__init__(self) # initialize parent
        self.textctrl = textctrl

    def emit(self, record):
        msg = self.format(record)
        self.textctrl.config(state="normal")
        self.textctrl.insert("end", msg + "\n")
        self.flush()
        self.textctrl.config(state="disabled")
        

