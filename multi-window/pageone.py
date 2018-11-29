# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 11:56:44 2018

@author: David Lindsey
"""
import tkinter as tk

#get other pages for navigation
import startpage
import pagetwo




LARGE_FONT= ("Verdana", 12)

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(startpage.StartPage))
        button1.pack()

        button2 = tk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(pagetwo.PageTwo))
        button2.pack()