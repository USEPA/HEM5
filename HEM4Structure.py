# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 12:17:06 2018

@author: David Lindsey
"""

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
from startpage import StartPage
from navigation import Navigation
from hem4Window import Hem4
from riskSummary import Summary

import queue



LARGE_FONT= ("Verdana", 20)
TEXT_FONT= ("Verdana", 15)



class HEM4Structure(tk.Tk):
    """
    This is the application structure for HEM4
    """

    def __init__(self, messageQueue, callbackQueue, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        
        self.frames = {}

        for F in (StartPage, Navigation, Hem4, Summary):
             if F == Hem4:
                
                frame = F(container, self, messageQueue, callbackQueue)
                 
                self.frames[F] = frame

                frame.grid(row=0, column=0, sticky="nsew")
             
             else: 

                frame = F(container, self)
    
                self.frames[F] = frame
    
                frame.grid(row=0, column=0, sticky="nsew")
            
           

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()
        
        
#    def after_callback(self):
#        """
#        Function listens on thread RUnning HEM4 for error and completion messages
#        logged via queue method
#        """
#        
#        try:
#            message = self.messageQueue.get(block=False)
#        except queue.Empty:
#            # let's try again later
#            self.after(25, self.after_callback)
#            return
#
#        print('after_callback got', message)
#        if message is not None:
#            self.scr.configure(state='normal')
#            self.scr.insert(tk.INSERT, message)
#            self.scr.insert(tk.INSERT, "\n")
#            self.scr.configure(state='disabled')
#            self.after(25, self.after_callback)


if __name__ == "__main__":
    

    
    messageQueue = queue.Queue()
    callbackQueue = queue.Queue()

    app = HEM4Structure(messageQueue, callbackQueue)
    app.title('HEM4')
    app.configure(background='green')
    
#    app.after(25, app.after_callback)
#    app.after(500, app.check_processing)
    
    app.mainloop()