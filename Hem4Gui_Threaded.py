# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 10:26:13 2017

@author: dlindsey
"""
#%% Imports

import os
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from tkinter import scrolledtext
import pandas as pd
import numpy as np
import Hem4_Input_Processing as prepare
from threading import Thread
import create_multi_kml as cmk
import sys
import queue
import HEM4_Runstream as rs
import subprocess
import Hem4_Output_Processing as po 
import math
import shutil

#%% excel file extension list to check

def is_excel(filepath):
    
    excel = [".xls", ".xlsx"]
    
    for extension in excel:
        if extension in filepath:
            return True
        else:
            return False
        

#%% Hem4 GUI

class Hem4():
    def __init__ (self):
        #create window instance
        self.win = tk.Tk()
    
        #title
        self.win.title("HEM4")
        self.win.maxsize(1000, 1000)
        self.createWidgets()
        self.running = False

#%% Quit Function    
    def quit_gui(self):
        if self.running == False:
            self.win.quit()
            self.win.destroy()
            exit()
        else:
             override = messagebox.askokcancel("Confirm HEM4 Quit", "Are you sure? Hem4 is currently running. Clicking 'OK' will stop HEM4.")
             if override == True:
                self.win.quit()
                self.win.destroy()
                exit()
            
#%%Create Widgets
    
    def createWidgets(self):
        # Tab Control introduced here --------------------------------------
        self.tabControl = ttk.Notebook(self.win)     # Create Tab Control

        tab1 = ttk.Frame(self.tabControl)            # Create a tab
        self.tabControl.add(tab1, text='HEM4')      # Add the tab

        tab2 = ttk.Frame(self.tabControl)            # Add a second tab
        self.tabControl.add(tab2, text='Log')      # Make second tab visible

        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible
        
         # Create container frame to hold all other widgets
        self.main = ttk.LabelFrame(tab1, text='HEM4 Upload Options ')
        self.main.grid(column=0, row=1)
        
        #create discreet sections for GUI in tab1
        self.s1 = tk.Frame(self.main, width=250, height=50)
        self.s2 = tk.Frame(self.main, width=250, height=100)
        self.s3 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
        self.s4 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
        self.s5 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
        self.s6 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
        self.s7 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
        self.s8 = tk.Frame(self.main, width=250, height=200)
        self.s9 = tk.Frame(self.main, width=250)
        #self.s10 = tk.Frame(self.main, width=250, height=200)

        self.s1.grid(row=0)
        self.s2.grid(row=1, column=0, sticky="nsew")
        self.s3.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.s4.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.s5.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.s6.grid(row=5, column=0, columnspan=2, sticky="nsew")
        self.s7.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.s8.grid(row=7, column=0, sticky="nsew")
        self.s9.grid(row=8, column=0, sticky="nsew")
        #self.s10.grid(row=9, column=0, sticky="nsew")

        self.main.grid_rowconfigure(9, weight=4)
        self.main.grid_columnconfigure(2, weight=1)
        self.s2.grid_propagate(0)
        #self.s1.grid_propagate(0)
    
        # create container frame to hold log
        self.log = ttk.LabelFrame(tab2, text=' Hem4 Progress Log ')
        self.log.grid(column=0, row=0)
        # Adding a Textbox Entry widget
        scrolW  = 65; scrolH  =  40
        self.scr = scrolledtext.ScrolledText(self.log, width=scrolW, height=scrolH, wrap=tk.WORD)
        self.scr.grid(column=0, row=3, sticky='WE', columnspan=3)
        
#%% Set Quit and Run buttons        
        self.quit = tk.Button(self.main, text="QUIT", fg="red",
                              command=self.quit_gui)
        self.quit.grid(row=9, column=0, sticky="W")
        
        #run only appears once the required files have been set
        self.run_button = tk.Button(self.main, text='RUN', fg="green", command=self.runThread).grid(row=9, column=1, sticky="E")
        
#%% Setting up  directions text space

        #Dynamic instructions place holder
        global instruction_instance
        instruction_instance = tk.StringVar(self.s2)
        instruction_instance.set(" ")
        self.dynamic_inst = ttk.Label(self.s2, wraplength=375, font="-size 9")
        
        self.dynamic_inst["textvariable"] = instruction_instance 
        self.dynamic_inst.grid(row = 2, sticky='ew', padx = 10)
        
        
        
# %% Setting up each file upload space (includes browse button, and manual text entry for file path)         
        
        #facilities label
        fac_label = tk.Label(self.s3, font="-size 10", text="Please select a Facilities List Options file (required):                                      ")
        fac_label.grid(row=1, sticky="W")
        
        #facilities upload button
        self.fac_up = ttk.Button(self.s3, command = lambda: self.upload("facilities options list"))
        self.fac_up["text"] = "Browse"
        self.fac_up.grid(row=2, column=0, sticky="W")
        self.fac_up.bind('<Enter>', lambda e:self.browse("instructions/fac_browse.txt"))
       
        #facilities text entry
        self.fac_list = tk.StringVar(self.s3)
        self.fac_list_man = ttk.Entry(self.s3)
        self.fac_list_man["width"] = 55
        self.fac_list_man["textvariable"]= self.fac_list
        self.fac_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.fac_list_man.bind('<Button-1>', lambda e:self.manual("instructions/fac_man.txt"))
        
                
        #Hap emissions label
        hap_label = tk.Label(self.s4, font="-size 10",  text="Please select a HAP Emissions file(required):                                                  ")
        hap_label.grid(row=1, sticky="W")
        
        #hap emissions upload button
        self.hap_up = ttk.Button(self.s4, command = lambda: self.upload("hap emissions"))
        self.hap_up["text"] = "Browse"
        self.hap_up.grid(row=2, column=0, sticky='W')
        #event handler for instructions (Button 1 is the left mouse click)
        self.hap_up.bind('<Enter>', lambda e:self.browse("instructions/hap_browse.txt"))
                
        #hap emission text entry
        self.hap_list = tk.StringVar(self.s4)
        self.hap_list_man = ttk.Entry(self.s4)
        self.hap_list_man["width"] = 55
        self.hap_list_man["textvariable"]= self.hap_list
        self.hap_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.hap_list_man.bind('<Button-1>', lambda e:self.manual("instructions/hap_man.txt"))
        
        
        #Emissions location label
        emisloc_label = tk.Label(self.s5, font="-size 10",  text="Please select an Emissions Locations file(required):                                         ")
        emisloc_label.grid(row=1, sticky="W")
        
        #emissions location upload button
        self.emisloc_up = ttk.Button(self.s5, command= lambda: self.upload("emissions locations"))
        self.emisloc_up["text"] = "Browse"
        self.emisloc_up.grid(row=2, column=0, sticky='W')
        #event handler for instructions (Button 1 is the left mouse click)
        self.emisloc_up.bind('<Enter>', lambda e:self.browse("instructions/emis_browse.txt"))
      
        #emission loccation file text entry
        self.emisloc_list = tk.StringVar(self.s5)
        self.emisloc_list_man = ttk.Entry(self.s5)
        self.emisloc_list_man["width"] = 55
        self.emisloc_list_man["textvariable"]= self.emisloc_list
        self.emisloc_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.emisloc_list_man.bind('<Button-1>', lambda e:self.manual("instructions/emis_man.txt"))
        
        
        #Polygon sources label
        poly_label = tk.Label(self.s6, font="-size 10",  text="Please select a Polygon Vertex file (if included):")
        poly_label.grid(row=1, sticky="W")
        
        #polygon sources upload button
        self.poly_up = ttk.Button(self.s6, command=lambda: self.upload("polyvertex") )
        self.poly_up["text"] = "Browse"
        self.poly_up.grid(row=2, column=0, sticky="W")
        #event handler for instructions (Button 1 is the left mouse click)
        self.poly_up.bind('<Enter>', lambda e:self.browse("instructions/poly_inst.txt"))
       
        #polygon sources loccation file text entry
        self.poly_list = tk.StringVar(self.s6)
        self.poly_list_man = ttk.Entry(self.s6)
        self.poly_list_man["width"] = 55
        self.poly_list_man["textvariable"]= self.poly_list
        self.poly_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.poly_list_man.bind('<Button-1>', lambda e:self.manual("instructions/poly_inst.txt"))
        
        
        #Buoyant Line  label
        bouyant_label = tk.Label(self.s7, font="-size 10",  text="Please select a Bouyant Line Source Parameter file (if included):")
        bouyant_label.grid(row=1, sticky="W")
        
        #bouyant line file upload button
        self.bouyant_up = ttk.Button(self.s7, command= lambda: self.upload("bouyant line"))
        self.bouyant_up["text"] = "Browse"
        self.bouyant_up.grid(row=2, column=0, sticky='W')
        #event handler for instructions (Button 1 is the left mouse click)
        self.bouyant_up.bind('<Enter>', lambda e:self.browse("instructions/bouyant_inst.txt"))
                
        #bouyant line file text entry
        self.bouyant_list = tk.StringVar(self.s7)
        self.bouyant_list_man = ttk.Entry(self.s7)
        self.bouyant_list_man["width"] = 55
        self.bouyant_list_man["textvariable"]= self.bouyant_list
        self.bouyant_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.bouyant_list_man.bind('<Button-1>', lambda e:self.manual("instructions/bouyant_inst.txt"))
        
        
        #csv output label
        #self.csv_label = tk.Label(self.s8, font="-size 10",  text="Select to output DBF files in CSV format")
        #self.csv_label.grid(row=2, column=0, sticky="W")
        
        #csv output
        #self.csv= tk.BooleanVar()
        #self.csv.set(False)
        #self.csv_output = ttk.Checkbutton(self.s8, variable=self.csv, command=self.csv_sel).grid(row=2, column=1, sticky="w")
        
        
        #optional input labels
        self.optional_label = tk.Label(self.s8, font="-size 10",  text="OPTIONAL Input Files", pady=10)
        self.optional_label.grid(row=0, column=1, sticky="W")
        
        #user receptors
        self.u_receptors= tk.BooleanVar()
        self.u_receptors.set(False)
        self.ur_op = ttk.Checkbutton(self.s8, text="Include user receptors for any facilities, as indicated in the Facilities List Options file.", variable=self.u_receptors, command=self.add_ur).grid(row=1, column=1, sticky="w")
        
        #building downwash
        self.building= tk.BooleanVar()
        self.building.set(False)
        self.downwash_op = ttk.Checkbutton(self.s8, text="Include building downwash for any facilities, as indicated in the Facilities List Options file.", variable=self.building, command=self.add_downwash).grid(row=3, column=1, sticky="w")
        
        #deposition/depletion
        self.depdep= tk.BooleanVar()
        self.depdep.set(False)
        self.dep_op = ttk.Checkbutton(self.s8,  text="Include deposition or depletion for any facilities, as indicated in the Facilities List Options file.", variable=self.depdep, command=self.add_dep).grid(row=5, column=1, sticky="W")
        
        #emission variation
        self.emis_var = tk.BooleanVar()
        self.emis_var.set(False)
        self.emis_var_op = ttk.Checkbutton(self.s8, text="Vary the emission inputs for one or more facilities.", variable=self.emis_var, command=self.add_emis_var).grid(row=7, column=1, sticky="w")        
        
        
        #temporal variations for ambient conentration
        self.temp_var = tk.BooleanVar()
        self.temp_var.set(False)
        self.temp_var_op = ttk.Checkbutton(self.s8, text='Generate output file showing temporal variations in ambient concentration results.', variable=self.temp_var, command=self.add_temp_var).grid(row=9, column=1, sticky="w")
        
        
         #%% Dynamic inputs for adding options

    def add_downwash(self):
        
        #when box is checked add row with input
        if self.building.get() == True:
            
            #user recptors upload button
            self.bd = ttk.Button(self.s8, command= lambda: self.upload("building downwash"))
            self.bd["text"] = "Browse"
            self.bd.grid(row=4, column=1, sticky="W")
            self.bd.bind('<Enter>', lambda e:self.browse("instructions/bd_browse.txt"))
            
            #user receptor text entry
            self.bd_list = tk.StringVar(self.s8)
            self.bd_list_man = ttk.Entry(self.s8)
            self.bd_list_man["width"] = 55
            self.bd_list_man["textvariable"]= self.bd_list
            self.bd_list_man.grid(row=4, column=1, sticky='E', padx =10)
            #event handler for instructions (Button 1 is the left mouse click)
            self.bd_list_man.bind('<Button-1>', lambda e:self.manual("instructions/bd_man.txt"))
            
            
        if self.building.get() == False:
            self.bd.destroy()
            self.bd_list_man.destroy()
            

    def add_ur(self):
        #when box is checked add row with input
        if self.u_receptors.get() == True:
            
            #user recptors upload button
            self.urep = ttk.Button(self.s8, command = lambda: self.upload("user receptors"))
            self.urep["text"] = "Browse"
            self.urep.grid(row=2, column=1, sticky="W", padx=10)
            self.urep.bind('<Enter>', lambda e:self.browse("instructions/urep_browse.txt"))
            
            #user receptor text entry
            self.urep_list = tk.StringVar(self.s8)
            self.urep_list_man = ttk.Entry(self.s8)
            self.urep_list_man["width"] = 55
            self.urep_list_man["textvariable"]= self.urep_list
            self.urep_list_man.grid(row=2, column=1, sticky='E', padx=85)
            #event handler for instructions (Button 1 is the left mouse click)
            self.urep_list_man.bind('<Button-1>', lambda e:self.manual("instructions/urep_man.txt"))
            
            
        if self.u_receptors.get() == False:
            self.urep.destroy()
            self.urep_list_man.destroy()

    #optional depletion
    def add_dep(self):
       
        
        if self.depdep.get() == True:
            
            #set up input sections
            
            self.s11 = tk.Label(self.main, text='Deposition and Depletion Options')
            self.s12 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
            self.s13 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
            self.s14 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
            self.s15 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
            
            
            if self.emis_var.get() == False:
                
                self.s11.grid(row=1, column=1, sticky="nsew")
                self.s12.grid(row=2, column=1, columnspan=2, sticky="nsew")
                self.s13.grid(row=3, column=1, columnspan=2, sticky="nsew")
                self.s14.grid(row=4, column=1, columnspan=2, sticky="nsew")
                
            elif self.emis_var.get() == True:
                if self.s16.grid_info()['row'] == 1:
                
                    self.s11.grid(row=3, column=1, sticky="nsew")
                    self.s12.grid(row=4, column=1, columnspan=2, sticky="nsew")
                    self.s13.grid(row=5, column=1, columnspan=2, sticky="nsew")
                    self.s14.grid(row=6, column=1, columnspan=2, sticky="nsew")
                
 
            #optional input file upload
                
            #particle deposition label
            part_label = tk.Label(self.s12, font="-size 10", text="Upload the file containing size information for particle matter emissions:")
            part_label.grid(row=1, sticky="W")
        
            #particle deposition upload button
            self.dep_part_up = ttk.Button(self.s12, command= lambda: self.upload("particle depletion"))
            self.dep_part_up["text"] = "Browse"
            self.dep_part_up.grid(row=2, column=0, sticky="W")
            self.dep_part_up.bind('<Enter>', lambda e:self.browse("instructions/dep_part_browse.txt"))
             
            #particle deposition  text entry
            self.dep_part = tk.StringVar(self.s12)
            self.dep_part_man = ttk.Entry(self.s12)
            self.dep_part_man["width"] = 55
            self.dep_part_man["textvariable"]= self.dep_part
            self.dep_part_man.grid(row=2, column=0, sticky='E', padx=85)
            #event handler for instructions (Button 1 is the left mouse click)
            self.dep_part_man.bind('<Button-1>', lambda e:self.manual("instructions/dep_part_man.txt"))
              
        
            #land use description label
            land_label = tk.Label(self.s13, font="-size 10",  text="Upload the file containing land use descriptions:")
            land_label.grid(row=1, sticky="W")
        
            #land use description upload button
            self.dep_land_up = ttk.Button(self.s13, command= lambda: self.upload("land use description"))
            self.dep_land_up["text"] = "Browse"
            self.dep_land_up.grid(row=2, column=0, sticky='W')
            #event handler for instructions (Button 1 is the left mouse click)
            self.dep_land_up.bind('<Enter>', lambda e:self.browse("instructions/dep_land_browse.txt"))
        
        
            #land use description text entry
            self.dep_land = tk.StringVar(self.s13)
            self.dep_land_man = ttk.Entry(self.s13)
            self.dep_land_man["width"] = 55
            self.dep_land_man["textvariable"]= self.dep_land
            self.dep_land_man.grid(row=2, column=0, sticky='E', padx=85)
            #event handler for instructions (Button 1 is the left mouse click)
            self.dep_land_man.bind('<Button-1>', lambda e:self.manual("instructions/dep_land_man.txt"))
        
        
            #seasonal vegetation label
            veg_label = tk.Label(self.s14, font="-size 10",  text="Upload the file defining the seasonal vegetative cover:")
            veg_label.grid(row=1, sticky="W")
        
             #seasonal vegetation location upload button
            self.dep_veg_up = ttk.Button(self.s14, command= lambda: self.upload("season vegetation") )
            self.dep_veg_up["text"] = "Browse"
            self.dep_veg_up.grid(row=2, column=0, sticky='W')
            #event handler for instructions (Button 1 is the left mouse click)
            self.dep_veg_up.bind('<Enter>', lambda e:self.browse("instructions/dep_veg_browse.txt"))
      
            #seasonal vegetation file text entry
            self.dep_veg = tk.StringVar(self.s14)
            self.dep_veg_man = ttk.Entry(self.s14)
            self.dep_veg_man["width"] = 55
            self.dep_veg_man["textvariable"]= self.dep_veg
            self.dep_veg_man.grid(row=2, column=0, sticky='E', padx=85)
            #event handler for instructions (Button 1 is the left mouse click)
            self.dep_veg_man.bind('<Button-1>', lambda e:self.manual("instructions/dep_veg_man.txt"))
                 
        if self.depdep.get() == False:
            self.s11.destroy()
            self.s12.destroy()
            self.s13.destroy()
            self.s14.destroy()
            
            
    def add_emis_var(self):
        #when box is checked add row with input
        if self.emis_var.get() == True:
            
     
            self.s16 = tk.Label(self.main, text='Emissions Variation Options')
            self.s17 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
               
                
            if self.depdep.get() == False:
                
                self.s16.grid(row=1, column=1, sticky="nsew")
                self.s17.grid(row=2, column=1, columnspan=2, sticky="nsew")
               
               
            elif self.depdep.get() == True:
            
                if self.s11.grid_info()['row'] == 1: 
                 
                    self.s16.grid(row=5, column=1, sticky="nsew")
                    self.s17.grid(row=6, column=1, columnspan=2, sticky="nsew")
            
            
            #emissions variation label
            emis_label = tk.Label(self.s17, font="-size 10", text="Upload the file containing emissions varations:")
            emis_label.grid(row=1, sticky="W")
        
            
            #emissions variation upload button
            self.evar = ttk.Button(self.s17)
            self.evar["text"] = "Browse"
            #self.evar["command"] = self.upload_evar
            self.evar.grid(row=2, column=0, sticky="W")
            #self.urep.bind('<Enter>', lambda e:self.emis_var_browse())
            
            #emissions varation text entry
            self.evar_list = tk.StringVar(self.s17)
            self.evar_list_man = ttk.Entry(self.s17)
            self.evar_list_man["width"] = 55
            self.evar_list_man["textvariable"]= self.evar_list
            self.evar_list_man.grid(row=2, column=0, sticky='E', padx=85)
            #event handler for instructions (Button 1 is the left mouse click)
            #self.evar_list_man.bind('<Button-1>', lambda e:self.emis_var_man())
             
            
        if self.emis_var.get() == False:
            self.s16.destroy()
            self.s17.destroy()
            
        
    def add_temp_var(self):
        
        if self.temp_var.get() == True:
            
            
            #
            #self.s19 = tk.Frame(self.main, width=250, height=100, padx=20, pady=50)
            #self.s18.grid(row=7, column=1, sticky="nsew")
            #self.s19.grid(row=7, column=2, columnspan=2, sticky="nsew")
            
            self.diurnal = tk.Label(self.s9, text='Diurnal resolution for the output file (scroll):').grid(row=1, column=1)
            hourlist= ('1 hr', '2 hrs', '3 hrs', '4 hrs', '6 hrs', '8 hrs', '12 hrs', '24 hrs' )
            hours = tk.StringVar(value=hourlist)
            #listbox of diurnal resolutions
            self.lbox = tk.Listbox(self.s9, listvariable=hours, height=3)
            self.lbox.grid(row=1, column=2)
             
            
        if self.temp_var.get() == False:
            self.diurnal.destroy()
            self.lbox.s19.destroy()
        

        
        #%% Specific upload functions for selecting each file, once selected convert excel file to dataframe
   
    def upload(self, file):
        """ The upload funtion takes a file string triggered by a button in the GUI, it then uses that to determine which type of file to unload """
    
        #checks
        if file == "polyvertex":
        
            if hasattr(self, "emisloc_df"): 
                filename = askopenfilename()
            else:
                messagebox.showinfo("Emissions Locations File Missing", "Please upload an Emissions Locations file before adding a Polyvertex file.")
        
        elif file == "bouyant":
           
            if hasattr(self, "emisloc_df"): 
                filename = askopenfilename()
            else:
                messagebox.showinfo("Emissions Locations File Missing", "Please upload an Emissions Locations file before adding a Bouyant line file.")
        
    
        elif file == "user receptors":
            
            if hasattr(self, "faclist_df"): 
                filename = askopenfilename()
            else:
                messagebox.showinfo("Facilities List Option File Missing", "Please upload a Facilities List Options file before selecting a User Receptors file.")
        
        else:
            #get file name from open dialogue
            filename = askopenfilename()
        
        #if the upload is canceled 
        if filename is None:
            print("Canceled!")
            #eventually open box or some notification to say this is required 
        elif is_excel(filename) is False:
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for " + file +".")
        elif is_excel(filename) is True:
            file_path = os.path.abspath(filename)
                          
            if file == "facilities options list":
                #make sure its a facilities list option file
                
                self.fac_list.set(file_path)
                self.fac_path = file_path
                
                #   FACILITIES LIST excel to dataframe
    
                self.faclist_df = pd.read_excel(open(self.fac_path,'rb')
                    , names=("fac_id","met_station","rural_urban","max_dist","model_dist"
                            ,"radial","circles","overlap_dist","acute","hours"
                            ,"elev","multiplier","ring1","dep","depl","phase"
                            ,"pdep","pdepl","vdep","vdepl","all_rcpts","user_rcpt"
                            ,"bldg_dw","urban_pop","fastall")
                    , converters={"fac_id":str,"met_station":str,"rural_urban":str
                            ,"acute":str
                            ,"elev":str,"dep":str,"depl":str,"phase":str
                            ,"pdep":str,"pdepl":str,"vdep":str,"vdepl":str,"all_rcpts":str,"user_rcpt":str
                            ,"bldg_dw":str,"fastall":str})
        
                #manually convert fac_list to numeric
                self.faclist_df["model_dist"] = pd.to_numeric(self.faclist_df["model_dist"],errors="coerce")
                self.faclist_df["radial"] = pd.to_numeric(self.faclist_df["radial"],errors="coerce")
                self.faclist_df["circles"] = pd.to_numeric(self.faclist_df["circles"],errors="coerce")
                self.faclist_df["overlap_dist"] = pd.to_numeric(self.faclist_df["overlap_dist"],errors="coerce")
                self.faclist_df["hours"] = pd.to_numeric(self.faclist_df["hours"],errors="coerce")
                self.faclist_df["multiplier"] = pd.to_numeric(self.faclist_df["multiplier"],errors="coerce")
                self.faclist_df["ring1"] = pd.to_numeric(self.faclist_df["ring1"],errors="coerce")
                self.faclist_df["urban_pop"] = pd.to_numeric(self.faclist_df["urban_pop"],errors="coerce")
                self.faclist_df["max_dist"] = pd.to_numeric(self.faclist_df["max_dist"],errors="coerce")
                
                #grab facility ideas for comparison with hap emission and emission location files
                self.facids = self.faclist_df['fac_id']
                    
                self.scr.insert(tk.INSERT, "Uploaded facilities options list file for " + str(self.facids.count()) + " facilities" )
                self.scr.insert(tk.INSERT, "\n")
                
            elif file == "hap emissions":
                    
                self.hap_list.set(file_path)
                self.hap_path = file_path
                
                #HAP EMISSIONS excel to dataframe    
                self.hapemis_df = pd.read_excel(open(self.hap_path, "rb")
                    , names=("fac_id","source_id","pollutant","emis_tpy","part_frac")
                    , converters={"fac_id":str,"source_id":str,"pollutant":str,"emis_tpy":float,"part_frac":float})
                
                #fill Nan with 0
                self.hapemis_df.fillna(0)
                
                #turn part_frac into a decimal
                self.hapemis_df['part_frac'] = self.hapemis_df['part_frac'] / 100
    
                #create additional columns, one for particle mass and the other for gas/vapor mass...
                self.hapemis_df['particle'] = self.hapemis_df['emis_tpy'] * self.hapemis_df['part_frac']
                self.hapemis_df['gas'] = self.hapemis_df['emis_tpy'] * (1 - self.hapemis_df['part_frac'])

    
               #get list of pollutants from dose library
                dose = pd.read_excel(open('resources/Dose_Response_Library.xlsx', 'rb'))
                master_list = list(dose['Pollutant'])
                lower = [x.lower() for x in master_list]
                
#                user_haps = set(self.hapemis_df['pollutant'])
#                
#                for hap in user_haps:
#                    if hap.lower() not in lower:
#                        print(hap)
                
          
                 
                missing_pollutants = {}
                for row in self.hapemis_df.itertuples():
                 
                    if row[3].lower() not in lower:
                        
                        if row[1] in missing_pollutants.keys():
                            
                            missing_pollutants[row[1]].append(row[3])
                            
                        else:
                            missing_pollutants[row[1]] = [row[3]]
                
                for key in missing_pollutants.keys():
                    missing_pollutants[key] = ', '.join(missing_pollutants[key])
                    
                
                #if there are any missing pollutants
                if len(missing_pollutants) > 0:
                    fix_pollutants = messagebox.askyesno("Missing Pollutants in dose response library", "The following pollutants were not found in HEM4's Dose Response Library: " + str(missing_pollutants) + ".\n Would you like to add them to the dose response library in the resources folder (they will be removed oherwise). ")
                    #if yes, clear box and empty dataframe
                   
                    
                    if fix_pollutants is True:
                        #clear hap emis upload area
                         self.hap_list.set('')
                         self.hap_path = file_path
                    
                        
                    #if no, remove them from dataframe 
                    elif fix_pollutants is False:
                        missing = list(missing_pollutants.values())
                        remove = set(missing[0].split(', '))
                        
    
                        #remove them from data frame
                        
                        for p in remove:
                            
                            self.hapemis_df = self.hapemis_df[self.hapemis_df.pollutant != str(p)]
                            
                            #record upload in log
                            #add another essage to say the following pollutants were assigned a generic value...
                            self.scr.insert(tk.INSERT, "Removed " + p + " from hap emissions file" )
                            self.scr.insert(tk.INSERT, "\n")
                        
                else:
                        #record upload in log
                    hap_num = set(self.hapemis_df['fac_id'])
                    self.scr.insert(tk.INSERT, "Uploaded HAP emissions file for " + str(len(hap_num)) + " facilities" )
                    self.scr.insert(tk.INSERT, "\n")
                
                
            elif file == "emissions locations":
                    
                self.emisloc_list.set(file_path)
                self.emisloc_path = file_path
                  
                    #EMISSIONS LOCATION excel to dataframe
                self.emisloc_df = pd.read_excel(open(self.emisloc_path, "rb")
                , names=("fac_id","source_id","location_type","lon","lat","utmzone","source_type"
                         ,"lengthx","lengthy","angle","horzdim","vertdim","areavolrelhgt","stkht"
                         ,"stkdia","stkvel","stktemp","elev","x2","y2")
                , converters={"fac_id":str,"source_id":str,"location_type":str,"lon":float,"lat":float
                        ,"utmzone":float,"source_type":str,"lengthx":float,"lengthy":float,"angle":float
                        ,"horzdim":float,"vertdim":float,"areavolrelhgt":float,"stkht":float,"stkdia":float
                        ,"stkvel":float,"stktemp":float,"elev":float,"x2":float,"y2":float})
                
                    #record upload in log
                emis_num = set(self.emisloc_df['fac_id'])
                self.scr.insert(tk.INSERT, "Uploaded emissions location file for " + str(len(emis_num)) + " facilities" )
                self.scr.insert(tk.INSERT, "\n")
                
                
            elif file == "polyvertex":
                
                self.poly_list.set(file_path)
                self.poly_path = file_path
                
                #POLYVERTEX excel to dataframe
                self.multipoly_df = pd.read_excel(open(self.poly_path, "rb")
                      , names=("fac_id","source_id","location_type","lon","lat","utmzone"
                               ,"numvert","area", "fipstct")
                      , converters={"fac_id":str,"source_id":str,"location_type":str,"lon":float
                                    ,"lat":float,"utmzone":str,"numvert":float,"area":float})
                
                #get polyvertex facility list for check
                find_is = self.emisloc_df[self.emisloc_df['source_type'] == "I"]
                fis = find_is['fac_id']
                    
                #check for unassigned polyvertex            
                check_poly_assignment = set(self.multipoly_df["fac_id"])
                poly_unassigned = []             
                
                for fac in fis:
                    if fac not in check_poly_assignment:   
                        poly_unassigned.append(fac)
                
                if len(poly_unassigned) > 0:
                    messagebox.showinfo("Unassigned Polygon Sources", "Polygon Sources for " + ", ".join(poly_unassigned) + " have not been assigned. Please edit the 'source_type' column in the Emissions Locations file.")
                    #clear box and empty data frame
                else:
                    #record upload in log
                    self.scr.insert(tk.INSERT, "Uploaded polygon sources for " + " ".join(check_poly_assignment))
                    self.scr.insert(tk.INSERT, "\n")
                
            
            elif file == "bouyant line":
                
                self.bouyant_list.set(file_path)
                self.bouyant_path = file_path
                
                #BOUYANT LINE excel to dataframe
                self.multibuoy_df = pd.read_excel(open(self.bouyant_path, "rb")
                      , names=("fac_id", "avgbld_len", "avgbld_hgt", "avgbld_wid", "avglin_wid", "avgbld_sep", "avgbuoy"))
            
                
                #get bouyant line facility list
                self.emisloc_df['source_type'].str.upper()
                find_bs = self.emisloc_df[self.emisloc_df['source_type'] == "B"]
                
                fbs = find_bs['fac_id'].unique()
                
                #check for unassigned buoyants
                 
                check_bouyant_assignment = set(self.multibuoy_df["fac_id"])
                
                bouyant_unassigned = []     
                for fac in fbs:
    
                    if fac not in check_bouyant_assignment: 
                        bouyant_unassigned.append(fac)
                
                if len(bouyant_unassigned) > 0:
                    messagebox.showinfo("Unassigned Bouyant Line parameters", "Bouyant Line parameters for " + ", ".join(bouyant_unassigned) + " have not been assigned. Please edit the 'source_type' column in the Emissions Locations file.")
                else:
                    #record upload in log
                    self.scr.insert(tk.INSERT, "Uploaded bouyant line parameters for " + " ".join(check_bouyant_assignment))
                    self.scr.insert(tk.INSERT, "\n")
                    
            
            elif file == "user receptors":
                
                file_path = os.path.abspath(filename)
                self.urep_list.set(file_path)
                self.urep_path = file_path
                
                #USER RECEPTOR dataframe
                self.ureceptr_df = pd.read_excel(open(self.urep_path, "rb")
                      , names=("fac_id", "loc_type", "lon", "lat", "utmzone", "elev", "rec_type", "rec_id"))
                
                #check for unassigned user receptors
                
                check_receptor_assignment = self.ureceptr_df["fac_id"]
                
                receptor_unassigned = []     
                for receptor in check_receptor_assignment:
                    #print(receptor)
                    row = self.faclist_df.loc[self.faclist_df['fac_id'] == receptor]
                    #print(row)
                    check = row['user_rcpt'] == 'Y'
                    #print(check)
                
                    if check is False:   
                        receptor_unassigned.append(str(receptor))
                
                
                if len(receptor_unassigned) > 0:
                    facilities = set(receptor_unassigned)
                    messagebox.showinfo("Unassigned User Receptors", "Receptors for " + ", ".join(facilities) + " have not been assigned. Please edit the 'user_rcpt' column in the facility options file.")
                else:
                    #record upload in log
                    self.scr.insert(tk.INSERT, "Uploaded user receptors for " + " ".join(check_receptor_assignment))
                    self.scr.insert(tk.INSERT, "\n")
            
            
            elif file == "building downwash":
                
                file_path = os.path.abspath(filename)
                self.bd_list.set(file_path)
                self.bd_path = file_path
                
                #building downwash dataframe
                self.bd_df = pd.read_csv(open(self.bd_path ,"rb"))
                
                 #record upload in log
                self.scr.insert(tk.INSERT, "Uploaded building downwash for...")
                self.scr.insert(tk.INSERT, "\n")
                
                
            elif file == "particle depletion":
                    
                file_path = os.path.abspath(filename)
                self.dep_part.set(file_path)
                self.dep_part_path = file_path
                
                #particle dataframe
                self.particle_df = pd.read_excel(open(self.dep_part_path, "rb")
                      , names=("fac_id", "source_id", "diameter", "mass", "density"))
                
                 #record upload in log
                self.scr.insert(tk.INSERT, "Uploaded particle depletion for...")
                self.scr.insert(tk.INSERT, "\n")
                
            elif file == "land use description":
                
                file_path = os.path.abspath(filename)
                self.dep_land.set(file_path)
                self.dep_land_path = file_path
                
                self.land_df = pd.read_excel(open(self.dep_land_path, "rb"))
                self.land_df.rename({"Facility ID " : "fac_id"})
                
                 #record upload in log
                self.scr.insert(tk.INSERT, "Uploaded land use description for...")
                self.scr.insert(tk.INSERT, "\n")
                
                
            elif file == "season vegetation":
                
                file_path = os.path.abspath(filename)
                self.dep_veg.set(file_path)
                self.dep_veg_path = file_path
                
                self.veg_df = pd.read_csv(open(self.dep_veg_path, "rb"))
                self.veg_df.rename({"Facility ID": "fac_id"})
                 #record upload in log
                self.scr.insert(tk.INSERT, "Uploaded season vegetation for...")
                self.scr.insert(tk.INSERT, "\n")
      
        
            elif file == "emissions variation":
                
                file_path = os.path.abspath(filename)
                self.evar_list.set(file_path)
                self.evar_list_path = file_path
                
                 #record upload in log
                self.scr.insert(tk.INSERT, "Uploaded emissions variance for...")
                self.scr.insert(tk.INSERT, "\n")
                
            
        
 #%% Event handlers for porting instructions

    #reset instructions space
    def reset_instructions(self):
        global instruction_instance
        instruction_instance.set(" ")    
        
    #general function for browsing instructions
    def browse(self, location):
        global instruction_instance
        read_inst = open(location, 'r')
        instruction_instance.set(read_inst.read())
        
    #general function for manual uploads    
    def manual(self, location):
        global instruction_instance
        read_inst = open(location, 'r')
        instruction_instance.set(read_inst.read())
    
    #csv option instructions
    def csv_sel(self):
        global instruction_instance
        read_inst = open("instructions/csv_inst.txt", 'r')
        instruction_instance.set(read_inst.read())
        
#%% check deposition and depletion settings function
    def check_dep(self, fac):
 #%% Particle ONLY
     #needs to be applied in a for loop or as an "apply + lambda function"
        dep_dplt = False
        
        if fac['phase'] == 'P': #particle
            
            #deposition only
            if fac['dep'] == 'Y' and fac['depl'] == 'nan':  #wet particle depostion only
                
                if fac['pdep'] == 'WO':
                    
                    #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WDEP NOWETDPLT']
                    else:
                         messagebox.showinfo("To run wet particle deposition only for facility id: " + fac['fac_id'] + " a particle size file is required.")
                        
                
                elif self.fac['pdep'] == 'DO': #dry particle deposition only
                    
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['DDEP NODRYDPLT']
                    else:
                         messagebox.showinfo("To run dry particle deposition only for facility id: " + fac['fac_id'] + " particle size, land_use, and season files are required.")
                    
                elif fac['pdep'] == 'WD': #wet and dry particle deposition
                    
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP NOWETDPLT NODRYDPLT']
                    else:
                         messagebox.showinfo("To run wet and dry particle deposition for facility id: " + fac['fac_id'] + " particle size, land use, and season files are required.")
            
            #depletion only
            elif fac['depl'] == 'Y' and fac['dep'] == 'nan':
            
                if fac['pdepl'] == 'WO': #wet particle depletion only
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WETDPLT']
                    else:
                         messagebox.showinfo("To run wet particle depletion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
                    
                    
                elif fac['pdepl'] == 'DO': #dry particle depletion only
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['DRYDPLT']
                    else:
                         messagebox.showinfo("To run dry particle depletion only for facility id:" + fac['fac_id'] + " a particle size file is required.")
                    
            
                elif fac['pdepl'] == 'WD': #wet and dry particle depletion
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WETDPLT DRYDPLT']
                    else:
                         messagebox.showinfo("To run wet and dry particle depletion for facility id:" + fac['fac_id'] + "a particle size file is required.")
                     
            #deposion with depletion
            elif fac['dep'] == 'Y' and fac['depl'] == 'Y':  
            
                if fac['pdep'] == 'WO' and fac['pdepl'] == 'WO': #wet particle only deposition and depletion
                
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = 'WDEP'
                    else:
                         messagebox.showinfo("To run wet particle only deposition and depletion for facility id:" + fac['fac_id'] + "a particle size file is required.")
                    
                elif fac['pdep'] == 'DO' and fac['pdepl'] == 'DO': #dry particle only deposition and depletion
                
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['DDEP']
                    else:
                         messagebox.showinfo("To run dry particle only deposition and depletion for facility id: " + fac['fac_id'] + " particle size, land use, and season files are required.")
            
                elif fac['pdep'] == 'WD' and fac['pdepl'] == 'WD': #wet and dry particle deposition and depletion
                
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP']
                    else:
                         messagebox.showinfo("To run wet and dry particle deposition and depletion for facility id: " + fac['fac_id'] + " particle size, land use, and season files are required.")
            
    #%% Vapor ONLY            
        elif fac['phase'] == 'V':
            
            #deposition only
            if fac['dep'] == 'Y' and fac['depl'] == 'nan': 
                
                if fac['vdep'] == 'WO': #wet vapor deposition only
                    keyword = ['WDEP NOWETDPLT']
                    #nothing?
                    
                elif fac['vdep'] == 'DO': #dry vapor deposition only
          
                    #check for land_use file, and seasons file
                    if  hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['DDEP NODRYDPLT']
                    else:
                         messagebox.showinfo("To run dry vapor deposition only for facility id: " + fac['fac_id'] + " land use and season files are required.")
                
                
                elif fac['vdep'] == 'WD': #wet and dry vapor deposition only
                    
                    #check for land_use file, and seasons file
                    if  hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP NOWETDPLT NODRYDPLT']
                    else:
                         messagebox.showinfo("To run wet and dry vapor deposition only for facility id: " + fac['fac_id'] + " a particle size file is required.")
                    
            #depletion only
            elif fac['depl'] == 'Y' and fac['dep'] == 'nan':
                
                if fac['vdepl'] == 'WO': #wet vapor depletion only
                #nothing?
                    keyword = ['WETDPLT']
                
                elif fac['vdepl'] == 'DO': #dry vapor depletion only
                #nothing?
                   keyword = ['DRYDPLT']
                
                elif fac['vdepl'] == 'WD': #wet and dry vapor depletion only
                #nothing?
                    keyword = ['WETDPLT DRYDPLT']
            
            #deposion with depletion
            elif fac['dep'] == 'Y' and fac['depl'] == 'Y':
                
                if fac['vdep'] == 'WO'  and fac['vdepl'] == 'WO': #vapor only deposition and depletion
                #nothing
                    keyword = ['WDEP']
                
                elif fac['vdep'] == 'DO' and fac['vdepl'] == 'DO':
                    
                    #check for land_use file, and seasons file
                    if  hasattr(self, 'land_df') and hasattr(self, 'veg_df'): #dry vapor depositon and depletion
                        dep_dplt = True
                        keyword = ['DDEP']
                    else:
                        messagebox.showinfo("To run dry vapor deposition and depletion for facility id: " + fac['fac_id'] + " land use and season files are required.")
            
                
                elif fac['vdep'] == 'WD' and fac['vdepl'] == 'WD': #wet and dry vapor deposition and depletion
                    
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP']
                    else:
                         messagebox.showinfo("To run wet and dry vapor deposition and depletion for facility id: " + fac['fac_id'] + " land use and season files are required.")
            
                
    #%% Particle and Vapor
        #deposition with depletion    
        elif fac['phase'] == 'B':
            
            #deposition only
            if fac['dep'] == 'Y' and fac['depl'] == 'nan': 
                
                if fac['pdep'] == 'WD' and fac['vdep'] == 'WD': #wet and dry particle, wet and dry vapor deposition only
                    
                #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP NOWETDPLT NODRYDPLT', 'WDEP DDEP NOWETDPLT NODRYDPLT']
                    else:
                         messagebox.showinfo("To run wet and dry particle and wey and dry vapor deposition only for facility id: " + fac['fac_id'] + " particle size, land use, and seasons files are required.")
            
                
                elif fac['pdep'] == 'WO' and fac['vdep'] == 'WO': #wet particle and wet vapor deposition only
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WDEP NOWETDPLT', 'WDEP NOWETDPLT']
                    else:
                         messagebox.showinfo("To run wet particle and wet vapor deposition only for facility id: " + fac['fac_id'] + " a particle size file is required.")
                
                elif fac['pdep'] == 'DO' and fac['vdep'] == 'DO': #dry particle and dry vapor deposition only
                    
                #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['DDEP NODRYDPLT', 'DDEP NODRYDPLT' ]
                    else:
                         messagebox.showinfo("To run dry particle and dry vapor deposition only for facility id: " + fac['fac_id'] + " particle size, land use, and seasons files are required.")
            
                
                elif fac['pdep'] == 'WO' and fac['vdep'] == 'DO': #wet particle and dry vapor deposition only
                    
                #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP NOWETDPLT', 'DDEP NOWETDPLT']
                    else:
                         messagebox.showinfo("To run wet particle ad dry vapor deposition only for facility id: " + fac['fac_id'] + " particle size, land use, and seasons files are required.")
            
                
                elif fac['pdep'] == 'DO' and fac['vdep'] == 'WO': #dry particle and wet vapor deposition only
                    
                    #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['DDEP NODRYDPLT', 'WDEP NOWETDPLT']
                    else:
                         messagebox.showinfo("To run dry particle and wet vapor depostion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
            
                elif fac['pdep'] == 'WD' and fac['vdep'] == 'WO': #wet and dry particle and wet vapor deposition only
                    
                    #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP NOWETDPLT NODRYDPLT', 'WDEP NOWETDPLT']
                    else:
                         messagebox.showinfo("To run wet and dry particle and wet vapor deposition only for facility id: " + fac['fac_id'] + " a particle size file is required.")
            
                elif fac['pdep'] == 'WD' and fac['vdep'] == 'DO': #wet and dry particle and dry vapor deposition only
                    
                #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP NOWETDPLT NODRYDPLT', 'DDEP NODRYDEPLT']
                    else:
                         messagebox.showinfo("To run wet and dry particle and wet vapor deposition only for facility id: " + fac['fac_id'] + " particle size, land use, and seasons files are required.")
            
                
                elif fac['pdep'] == 'WO' and fac['vdep'] == 'WD': #wet particle and wet and dry vapor deposition only
                    
                #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP NOWETDPLT', 'WDEP DDEP NOWETDPLT NODRYDPLT']
                    else:
                         messagebox.showinfo("To run wet particle and wet and dry vapor deposition only for facility id: " + fac['fac_id'] + " particle size, land use, and seasons files are required.")
            
            
                elif fac['pdep'] == 'DO' and fac['vdep'] == 'WD': #dry particle and wet and dry vapor deposition only
                    
                #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['DDEP NODRYDPLT', 'WDEP DDEP NOWETDPLT NODRYDPLT']
                    else:
                         messagebox.showinfo("To run dry particle and wet and dry vapor deposition only for facility id: " + fac['fac_id'] + " particle size, land use, and seasons files are required.")
            
            
                elif fac['pdep'] == 'WO' and fac['vdep'] == 'NO': #wet particle no vapor
                    
                 #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WDEP NOWETDPLT', 'None']
                    else:
                         messagebox.showinfo("To run wet particle deposition (no vapor) for facility id: " + fac['fac_id'] + " a particle size file is required.")
                 
                elif fac['pdep'] == 'DO' and fac['vdep'] == 'NO': #dry particle no vapor
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['DDEP NODRYDPLT', None]
                    else:
                         messagebox.showinfo("To run dry particle deposition (no vapor) for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                elif fac['pdep'] == 'WD' and fac['vdep'] == 'NO': #wet and dry particle no vapor
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP NOWETDPLT NODRYDPLT', None]
                    else:
                         messagebox.showinfo("To run wet and dry particle deposition (no vapor) for facility id: " + fac['fac_id'] + " a particle size file is required.")
    
                elif fac['pdep'] == 'NO' and fac['vdep'] == 'WO': #no particle, wet vapor
                    keyword = [None, 'WDEP NOWETDPLT']
                #nothing
    
                elif fac['pdep'] == 'NO' and fac['vdep'] == 'DO': #no particle, dry vapor
                    keyword = [None, 'DDEP NODRYDPLT']
                #land use, season
    
                elif fac['pdep'] == 'NO' and fac['vdep'] == 'WD': #no particle, wet and dry vapor
                    keyword = [None, 'WDEP DDEP NOWETDPLT NODRYDPLT']
                #land use, season
    
                elif fac['pdep'] == 'NO' and fac['vdep'] == 'NO': #no particle, no vapor (set to phase B)
                    keyword = [None, None]
                #nothing
            
                 
            #depletion only
            
            elif fac['depl'] == 'Y' and fac['dep'] == 'nan': 
               
                if fac['pdepl'] == 'WD' and fac['vdepl'] == 'WD': #wet and dry particle and wet and dry vapor depletion only
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WETDPLT DRYDPLT', 'WETDPLT DRYDPLT']
                    else:
                         messagebox.showinfo("To run wet and dry particle and wet and dry vapor depletion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                elif fac['pdepl'] == 'WO' and fac['vdepl'] == 'WO': #wet particle and wet vapor depletion only
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WETDPLT', 'WETDPLT']
                    else:
                         messagebox.showinfo("To run wet particle and wet vapor depletion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
            
                elif fac['pdepl'] == 'DO' and fac['vdepl'] == 'DO': #dry particle and dry vapor depletion only
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['DRYDPLT', 'DRYDPLT']
                    else:
                         messagebox.showinfo("To run dry particle and dry vapor depletion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                elif fac['pdepl'] == 'WO' and fac['vdepl'] == 'DO': #wet particle and dry vapor depletion only
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WETDPLT', 'DRYDPLT']
                    else:
                         messagebox.showinfo("To run wet particle and dry vapor depletion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                
                elif fac['pdepl'] == 'DO' and fac['vdepl'] == 'WO': #dry particle, wet vapor depletion only
                
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['DRYDPLT', 'WETDPLT']
                    else:
                         messagebox.showinfo("To run dry particle and wet vapor depletion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
                
                
                elif fac['pdepl'] == 'WD' and fac['vdepl'] == 'WO': #wet and dry particle and wet vapor depletion only
                   
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WETDPLT DRYDPLT', 'WETDPLT']
                    else:
                         messagebox.showinfo("To run wet and dry particle and wet vapor depletion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                elif fac['pdepl'] == 'WD' and fac['vdepl'] == 'DO': #wet and dry particle and dry vapor depletion only
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WETDPLT DRYDPLT', 'DRYDPLT']
                    else:
                         messagebox.showinfo("To run wet and dry particle and dry vapor depletion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
    
                elif fac['pdepl'] == 'WO' and fac['vdepl'] == 'WD': #wet particle and wet and dry vapor depletion only
                   
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WETDPLT', 'WETDPLT DRYDPLT']
                    else:
                         messagebox.showinfo("To run wet particle and wet and dry vapor depletion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                elif fac['pdepl'] == 'DO' and fac['vdepl'] == 'WD': #dry particle and wet and dry vapor depletion only
                   
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['DRYDPLT', 'WETDPLT DRYDPLT']
                    else:
                         messagebox.showinfo("To run dry particle and wet and dry vapor depletion only for facility id: " + fac['fac_id'] + " a particle size file is required.")
            
                elif fac['pdepl'] == 'WO' and fac['vdepl'] == 'NO': #wet particle no vapor depletion
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WETDPLT', None]
                    else:
                         messagebox.showinfo("To run wet particle (no vapor) depletion for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                elif fac['pdepl'] == 'DO' and fac['vdepl'] == 'NO': #dry particle no vapor depletion
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['DRYDPLT', None]
                    else:
                         messagebox.showinfo("To run dry particle (no vapor) depletion for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                elif fac['pdepl'] == 'WD' and fac['vdepl'] == 'NO': #wet and dry particle no vapor depletion
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WETDPLT DRYDPLT', None]
                    else:
                         messagebox.showinfo("To run wet and dry particle (no vapor) depletion for facility id: " + fac['fac_id'] + " a particle size file is required.")
            
                elif fac['pdepl'] == 'NO' and fac['vdepl'] == 'WO': #no particle wet vapor depletion only
                    keyword = [None, 'WETDPLT']
                #nothing
            
                elif fac['pdepl'] == 'NO' and fac['vdepl'] == 'DO': #no particle dry vapor depletion
                    
                #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = [None, 'DRYDPLT']
                    else:
                         messagebox.showinfo("To no particle dry vapor depletion only for facility id: " + fac['fac_id'] + " land use and season files are required.")
            
        
                elif fac['pdepl'] == 'NO' and fac['vdepl'] == 'WD': #no particle wet and dry vapor depletion only
                    
                #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = [None, 'WETPLT DRYDPLT']
                    else:
                         messagebox.showinfo("To run no particle wet and dry vapor depletion only for facility id: " + fac['fac_id'] + " land use and season files are required.")
            
        
                elif fac['pdepl'] == 'NO' and fac['vdepl'] == 'NO': #no vapor, no particle
                    
                #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = [None, None]
                    else:
                         messagebox.showinfo("To run no particle and no vapor depletion for facility id: " + fac['fac_id'] + " a particle size file is required.")
            
            #both desposition and depletion 
           
            elif fac['dep'] == 'Y' and fac['depl'] == 'Y':
        
                if fac['pdep'] == 'WD' and fac['vdep'] == 'WD' and fac['pdepl'] == 'WD' and fac['vdepl'] == 'WD': #wet and dry particle and wet and dry vapor deposition and depletion
                   
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP', 'WDEP DDEP']
                    else:
                         messagebox.showinfo("To run wet and dry particle and wet and dry vapor deposition and depletion for facility id: " + fac['fac_id'] + " particle size, land use, and season files are required.")
            
        
                elif fac['pdep'] == 'WO' and fac['vdep'] == 'WO' and fac['pdepl'] == 'WO' and fac['vdepl'] == 'WO': #wet particle and wet vapor deposition and depletion
                   
                    #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WDEP', 'WDEP']
                    else:
                         messagebox.showinfo("To run wet particle and wet vapor deposition and depletion for facility id: " + fac['fac_id'] + " a particle size file is required.")
            
                elif fac['pdep'] == 'DO' and fac['vdep'] == 'DO' and fac['pdepl'] == 'DO' and fac['vdepl'] == 'DO': #dry particle and dry vapor deposition and depletion
                    
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['DDEP', 'DDEP']
                    else:
                         messagebox.showinfo("To run dry particle and dry vapor deposition and depletion for facility id: " + fac['fac_id'] + " particle size, land use, and season files are required.")
        
                elif fac['pdep'] == 'WO' and fac['vdep'] == 'DO' and fac['pdepl'] == 'WO' and fac['vdepl'] == 'DO': #wet particle and dry vapor deposition and depletion
                   
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP', 'DDEP']
                    else:
                         messagebox.showinfo("To run wet particle and dry vapor deposition and depletion for facility id: " + fac['fac_id'] + " particle size, land use, and season files are required.")
        
                elif fac['pdep'] == 'DO' and fac['vdep'] == 'WO' and fac['pdepl'] == 'DO' and fac['vdepl'] == 'WO': #dry particle and wet vapor depostion and depletion
                    
                    #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['DDEP', 'WDEP']
                    else:
                         messagebox.showinfo("To run dry particle and wet vapor deposition and depletion for facility id: " + fac['fac_id'] + " a particle size file is required.")
            
                elif fac['pdep'] == 'WD' and fac['vdep'] == 'WO' and fac['pdepl'] == 'WD' and fac['vdepl'] == 'WO': #wet and dry particle and wet vapor deposition and depletion
                    
                    #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP', 'WDEP']
                    else:
                         messagebox.showinfo("To run wet and dry particle and wet vapor deposition and depletion for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                elif fac['pdep'] == 'WD' and fac['vdep'] == 'DO' and fac['pdepl'] == 'WD' and fac['vdepl'] == 'DO': #wet and dry particle and dry vapor deposition and depletion
                    
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP', 'DDEP']
                    else:
                         messagebox.showinfo("To run wet and dry particle and dry vapor deposition and depletion for facility id: " + fac['fac_id'] + " particle size, land use, and season files are required.")
                
                elif fac['pdep'] == 'WO' and fac['vdep'] == 'WD' and fac['pdepl'] == 'WO' and fac['vdepl'] == 'WD': #wet particle and wet and dry vapor
                    
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['WDEP', 'WDEP DDEP']
                    else:
                         messagebox.showinfo("To run wet particle and wet and dry vapor deposition and depletion for facility id: " + fac['fac_id'] + " particle size, land use, and season files are required.")
            
                elif fac['pdep'] == 'DO' and fac['vdep'] == 'WD' and fac['pdepl'] == 'DO' and fac['vdepl'] == 'WD': #dry particle and wet and dry vapor deposition and depletion
                    
                    #check for particle size file, land_use file, and seasons file
                    if  hasattr(self, 'particle_df') and hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = ['DDEP', 'WDEP DDEP']
                    else:
                         messagebox.showinfo("To run dry particle and wet and dry deposition and depletion for facility id: " + fac['fac_id'] + " particle size, land use, and season files are required.")
            
                elif fac['pdep'] == 'WO' and fac['vdep'] == 'NO' and fac['pdepl'] == 'WO' and fac['vdepl'] == 'NO': #wet particle, no vapor
                    
                    #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WDEP', None]
                    else:
                         messagebox.showinfo("To run wet particle (no vapor) deposition and depletion for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                elif fac['pdep'] == 'DO' and fac['vdep'] == 'NO' and fac['pdepl'] == 'DO' and fac['vdepl'] == 'NO': #dry particle no vapor
                    
                    #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['DDEP', None]
                    else:
                         messagebox.showinfo("To run dry particle (no vapor) deposition and depletion for facility id: " + fac['fac_id'] + " a particle size file is required.")
            
                elif fac['pdep'] == 'WD' and fac['vdep'] == 'NO' and fac['pdepl'] == 'WD' and fac['vdepl'] == 'NO': #wet and dry particle no vapor
                    
                    #check for particle size file
                    if  hasattr(self, 'particle_df'):
                        dep_dplt = True
                        keyword = ['WDEP DDEP', None]
                    else:
                         messagebox.showinfo("To run wet and dry particle (no vapor ) deposition and depletion for facility id: " + fac['fac_id'] + " a particle size file is required.")
        
                elif fac['pdep'] == 'NO' and fac['vdep'] == 'WO' and fac['pdepl'] == 'NO' and fac['vdepl'] == 'WO': #no particle and wet vapor deposition and depletion
                    keyword = [None, 'WDEP']
                    #nothing
        
                elif fac['pdep'] == 'NO' and fac['vdep'] == 'DO' and fac['pdepl'] == 'NO' and fac['vdepl'] == 'DO': #no particle and dry vapor deposition and depletion
                    
                    #check for land_use file, and seasons file
                    if hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = [None, 'DDEP']
                    else:
                         messagebox.showinfo("To run no particle and dry vapor deposition and depletion for facility id: " + fac['fac_id'] + " land use, and season files are required.")
        
                elif fac['pdep'] == 'NO' and fac['vdep'] == 'WD' and fac['pdepl'] == 'NO' and fac['vdepl'] == 'WD': #no particle and wet and dry vapor deposition and depletion
                    
                    #check for land_use file, and seasons file
                    if hasattr(self, 'land_df') and hasattr(self, 'veg_df'):
                        dep_dplt = True
                        keyword = [None, 'WDEP DDEP']
                    else:
                         messagebox.showinfo("To run no particle and wet and dry vapor deposition and depletion for facility id: " + fac['fac_id'] + " land use, and season files are required.")
        
                elif fac['pdep'] == 'NO' and fac['vdep'] == 'NO' and fac['pdepl'] == 'NO' and fac['vdepl'] == 'NO':
                    keyword = [None, None]
                    #nothing
            
            return keyword
             
            
            
        
             
#%% Run function with checks if somethign is missing raise the error here and create an additional dialogue before trying to run the file

    def run(self):
        
#%% check file dataframes
        
        ready = False
        
        #make sure fac_list df was created correctly
        if hasattr(self, "faclist_df"):
            
            if self.faclist_df.empty:
                messagebox.showinfo("Error","There was an error uploading Facilities List Option File, please try again")
                check1 = False
                
            else:
                fids = set(self.faclist_df['fac_id'])
                print("fac_list ready")
                check1 = True
        else:
            check1 = False
            messagebox.showinfo("Error","There was an error uploading Facilities List Option File, please try again")
       
        #make sure emis_loc df was created correctly
        if hasattr(self, "emisloc_df"):
            
            if self.emisloc_df.empty:
                messagebox.showinfo("Error","There was an error uploading Emissions Locations File, please try again")
                check2 = False
            else:
                #check facility id with emis loc ids
                efids = set(self.emisloc_df['fac_id'])
                esource = set(self.emisloc_df['source_id'])
                if efids == fids:
                    print("emis_locs ready")
                    check2 = True
                
        else:
            check2 = False
            messagebox.showinfo("Error","There was an error uploading Emissions Locations File, please try again")

       #make sure hap_emis  df was created correctly
        if hasattr(self, "hapemis_df"):
            print("found!")
            
            if self.hapemis_df.empty:
                messagebox.showinfo("Error","There was an error uploading HAP Emissions File, please try again")
                check3 = False
                print("empty")
            else:
                #check emis locations and source ids
                hfids = set(self.hapemis_df['fac_id'])
                hsource = set(self.hapemis_df['source_id'])
                missing_sources = []
                
                
                if efids == hfids:
                    print(True)
                    
                    for s in esource:
                        if s not in hsource:
                            missing_sources.append(s)
                    
                    if len(missing_sources) < 0:
                        check3 = False
                    
                    else:
                        check3 = True
                        print("hap_emis ready!")
                    
                else:
                    check3 = False
                
        else:
            check3 = False
            messagebox.showinfo("Error","There was an error uploading HAP Emissions File, please try again")
        
        if check1 == True & check2 == True & check3 == True:
        
            #if there isnt a file for poly vertex
            if  hasattr(self, 'multipoly_df'):
               pass 
            else: 
                self.multipoly_df = None    
           
            #if there isnt a file for bouyant line
            if  hasattr(self, 'multibuoy_df'):
                pass
            else:
                self.multibuoy_df = None
    
            #if there isnt a file for user receptors
            if  hasattr(self, 'ureceptr_df'):
                pass
            else:
                self.ureceptr_df = None
            
            #if building downwash
            if  hasattr(self, 'bd_path'):
                pass
            #    print("Building downwash file path: " + self.bd_path)
            else:
                self.bd_path = None
            
            #if depletion calculation
            if self.depdep == True:
                self.keyword = {}
                for row in self.fac_list.itterows():
                    self.keyword[row['fac_id']] = self.check_dep(row['fac_id'])
                
            
            
           #check user receptors in facility
            user_rec_check = self.faclist_df['user_rcpt'] == 'Y'
            user_rec_checklist = []
            
            if True in user_rec_check:
               for facility in self.faclist_df[user_rec_check]['fac_id']:
                   
                   if self.ureceptr_df is None:
                       
                       user_rec_checklist.append(str(facility))
                      
            if len(user_rec_checklist) > 0:
                messagebox.showinfo( "Missing user receptors", "Please upload user receptors for " + ", ".join(user_rec_checklist))
                ready = False   
            
            
            #check emissions list for bouyant line indicators   
            bouyant_check = self.emisloc_df["source_type"].str.upper() == "B"
            bouyant_checklist = []
    
            if True in bouyant_check:          
                for bfacility in self.emisloc_df[bouyant_check]['fac_id']:                
                    if self.multibuoy_df is None:                   
                        bouyant_checklist.append(str(bfacility))
            
            bfacilities = set(bouyant_checklist)            
            if len(bouyant_checklist) > 0:
                messagebox.showinfo("Missing bouyant line", "Please upload buoyant line file for " + ", ".join(bfacilities))
                ready = False
            
            #check emissions list for poly vertex indicators   
            polyvertex_check = self.emisloc_df["source_type"].str.upper() == "I"
            poly_checklist = []
    
            if True in polyvertex_check:          
                for pfacility in self.emisloc_df[polyvertex_check]['fac_id']:                
                    if self.multipoly_df is None:                   
                        poly_checklist.append(str(pfacility))
            
            pfacilities = set(poly_checklist)            
            if len(poly_checklist) > 0:
                messagebox.showinfo("Missing polyvertex", "Please upload polyvertex line file for " + ", ".join(pfacilities))
                ready = False
    
            
            if hasattr(self, 'multipoly_df') and hasattr(self, 'ureceptr_df') and hasattr(self, 'multibuoy_df'):
                self.ready = True
                print("Ready to run!")
        
        
        
       #%%if the object is ready
        if ready == True:
           
            #tell user to check the Progress/Log section
           
            
           #save version of this gui as is? constantly overwrite it once each facility is done?
           
           
           messagebox.askokcancel("Confirm HEM4 Run", "Clicking 'OK' will start HEM4.")
           
           #create object for prepare inputs
           self.running = True
           #create a Google Earth KML of all sources to be modeled
           createkml = cmk.multi_kml(self.emisloc_df, self.multipoly_df, self.multibuoy_df)
           if createkml is not None:
               source_map = createkml.create_sourcemap()
               kmlfiles = createkml.write_kml_emis_loc(source_map)

           
           the_queue.put("\nPreparing Inputs for " + str(self.facids.count()) + " facilities")
           pass_ob = prepare.Prepare_Inputs( self.faclist_df, self.emisloc_df, self.hapemis_df, self.multipoly_df, self.multibuoy_df, self.ureceptr_df)
           
           # let's tell after_callback that this completed
           #print('thread_target puts None to the queue')
           
           
           fac_list = []
           for index, row in pass_ob.faclist_df.iterrows():
            
               facid = row[0]
               fac_list.append(facid)
               num = 1
        
           for fac in fac_list:
                
                the_queue.put("\nRunning facility " + str(num) + " of " + str(len(fac_list)))
               
                facid = fac
                
                result = pass_ob.prep_facility(facid)
                
                the_queue.put("Building Runstream File for " + str(facid))

                result.build()
              
                #create fac folder
                fac_folder = "output/"+ str(facid) + "/"
                if not os.path.exists(fac_folder):
                    os.makedirs(fac_folder)
                 
                #run aermod
                the_queue.put("Running Aermod for " + str(facid))
                args = "aermod.exe aermod.inp" 
                subprocess.call(args, shell=False)
                
            #self.loc["textvariable"] = "Aermod complete for " + facid
            
            ## Check for successful aermod run:
                check = open('aermod.out','r')
                message = check.read()
                if 'AERMOD Finishes UN-successfully' in message:
                    success = False
                    the_queue.put("Aermod ran unsuccessfully. Please check the error section of the aermod.out file.")
                #increment facility count
                    num += 1 
                else:
                    success = True
                    the_queue.put("Aermod ran successfully.")
                check.close()    
                
                if success == True:
                    
                
            #move aermod.out to the fac output folder 
            #replace if one is already in there othewrwise will throw error
            
                    if os.path.isfile(fac_folder + 'aermod.out'):
                        os.remove(fac_folder + 'aermod.out')
                        shutil.move('aermod.out', fac_folder)
                
                    else:    
                        shutil.move('aermod.out', fac_folder)
            
            #process outputs
                    the_queue.put("Processing Outputs for " + str(facid))
                    process = po.Process_outputs(facid, pass_ob.haplib_df, result.hapemis, fac_folder, pass_ob.innerblks, pass_ob.outerblks, result.polar_df)
                    process.process()
                    the_queue.put("Finished calculations for " + str(facid) + "\n")
                #self.loc["textvariable"] = "Analysis Complete"
           
                #increment facility count
                    num += 1 
      
            
        self.running = False
        
        
#%% Create Thread for Threaded Process   
    def runThread(self):
        global instruction_instance
        instruction_instance.set("Hem4 Running, check the progress/log tab for updates")
        runT = Thread(target=self.run)
        runT.daemon = True
        runT.start()
        
        
    def after_callback(self):
        try:
            message = the_queue.get(block=False)
        except queue.Empty:
            # let's try again later
            hem4.win.after(25, self.after_callback)
            return

        print('after_callback got', message)
        if message is not None:
            self.scr.insert(tk.INSERT, message)
            self.scr.insert(tk.INSERT, "\n")
            hem4.win.after(25, self.after_callback)   
         
        
        

#%% Start GUI

the_queue = queue.Queue()


hem4 = Hem4()
hem4.win.after(25, hem4.after_callback)
hem4.win.mainloop()
