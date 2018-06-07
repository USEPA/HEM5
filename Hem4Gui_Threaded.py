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
import create_facililty_kml as fkml
import time


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
        elif self.running == True:
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
        #self.s6 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
        #self.s7 = tk.Frame(self.main, width=250, height=100, pady=10, padx=10)
        self.s8 = tk.Frame(self.main, width=250, height=200, pady=10, padx=10)
        self.s9 = tk.Frame(self.main, width=250, pady=10, padx=10)
        #self.s10 = tk.Frame(self.main, width=250, height=200)

        self.s1.grid(row=0)
        self.s2.grid(row=1, column=0, sticky="nsew")
        self.s3.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.s4.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.s5.grid(row=4, column=0, columnspan=2, sticky="nsew")
        #self.s6.grid(row=5, column=0, columnspan=2, sticky="nsew")
        #self.s7.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.s8.grid(row=5, column=0, sticky="nsew")
        self.s9.grid(row=6, column=0, sticky="nsew")
        #self.s10.grid(row=9, column=0, sticky="nsew")

        self.main.grid_rowconfigure(8, weight=4)
        self.main.grid_columnconfigure(2, weight=1)
        self.s2.grid_propagate(0)
        #self.s1.grid_propagate(0)
    
        # create container frame to hold log
        self.log = ttk.LabelFrame(tab2, text=' Hem4 Progress Log ')
        self.log.grid(column=0, row=0)
        # Adding a Textbox Entry widget
        scrolW  = 65; scrolH  =  25
        self.scr = scrolledtext.ScrolledText(self.log, width=scrolW, height=scrolH, wrap=tk.WORD)
        self.scr.grid(column=0, row=3, sticky='WE', columnspan=3)
        
#%% Set Quit and Run buttons        
        self.quit = tk.Button(self.main, text="QUIT", fg="red",
                              command=self.quit_gui)
        self.quit.grid(row=8, column=0, sticky="W")
        
        #run only appears once the required files have been set
        self.run_button = tk.Button(self.main, text='RUN', fg="green", command=self.runThread).grid(row=8, column=1, sticky="E")
        
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
        
  
        
        #optional input labels
        self.optional_label = tk.Label(self.s8, font="-size 10",  text="OPTIONAL Input Files", pady=10)
        self.optional_label.grid(row=0, column=1, sticky="W")
        
        #user receptors
        self.u_receptors= tk.BooleanVar()
        self.u_receptors.set(False)
        self.ur_op = ttk.Checkbutton(self.s8, text="Include user receptors for any facilities, as indicated in the Facilities List Options file.", variable=self.u_receptors, command=self.add_ur).grid(row=1, column=1, sticky="w")
        
        
        
         #%% Dynamic inputs for adding options


    def add_ur(self):
        #when box is checked add row with input
        if self.u_receptors.get() == True:
            
            #user recptors upload button
            self.urep = ttk.Button(self.s8, command = lambda: self.upload("user receptors"))
            self.urep["text"] = "Browse"
            self.urep.grid(row=2, column=1, sticky="W")
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
                
                user_haps = set(self.hapemis_df['pollutant'])
                missing_pollutants = []
                
                for hap in user_haps:
                    if hap.lower() not in lower:
                        missing_pollutants.append(hap)
                  
                 
#                missing_pollutants = {}
#                for row in self.hapemis_df.itertuples():
#                 
#                    if row[3].lower() not in lower:
#                        
#                        if row[1] in missing_pollutants.keys():
#                            
#                            missing_pollutants[row[1]].append(row[3])
#                            
#                        else:
#                            missing_pollutants[row[1]] = [row[3]]
#                
#                for key in missing_pollutants.keys():
#                    missing_pollutants[key] = ', '.join(missing_pollutants[key])
                    
                
                #if there are any missing pollutants
                if len(missing_pollutants) > 0:
                    fix_pollutants = messagebox.askyesno("Missing Pollutants in dose response library", "The following pollutants were not found in HEM4's Dose Response Library: " + ', '.join(missing_pollutants) + ".\n Would you like to add them to the dose response library in the resources folder (they will be removed oherwise). ")
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
                    check_receptor_assignment = [str(facility) for facility in check_receptor_assignment]
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
    
             
#%% Run function with checks if somethign is missing raise the error here and create an additional dialogue before trying to run the file

    def run(self):
        
#%% check file dataframes
        
        self.ready = False
        
        #make sure fac_list df was created correctly
        if hasattr(self, "faclist_df"):
            
            if self.faclist_df.empty:
                messagebox.showinfo("Error","There was an error uploading Facilities List Option File, please try again")
                check1 = False
                
            else:
                fids = set(self.faclist_df['fac_id'])
               # print("fac_list ready")
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
                    #print("emis_locs ready")
                    check2 = True
                
        else:
            check2 = False
            messagebox.showinfo("Error","There was an error uploading Emissions Locations File, please try again")

       #make sure hap_emis  df was created correctly
        if hasattr(self, "hapemis_df"):
            
            
            if self.hapemis_df.empty:
                messagebox.showinfo("Error","There was an error uploading HAP Emissions File, please try again")
                check3 = False
                #print("empty")
            else:
                #check emis locations and source ids
                hfids = set(self.hapemis_df['fac_id'])
                hsource = set(self.hapemis_df['source_id'])
                missing_sources = []
                
                
                if efids == hfids:
                    #print(True)
                    
                    for s in esource:
                        if s not in hsource:
                            missing_sources.append(s)
                    
                    if len(missing_sources) < 0:
                        check3 = False
                    
                    else:
                        check3 = True
                        #print("hap_emis ready!")
                    
                else:
                    check3 = False
                
        else:
            check3 = False
            messagebox.showinfo("Error","There was an error uploading HAP Emissions File, please try again")
        
        
        if check1 == True & check2 == True & check3 == True:
                
        
       
        
            
            #check user receptors in facility
            user_rec_check = self.faclist_df['user_rcpt'] == 'Y'
            user_rec_checklist = []
            
                
            if True in user_rec_check.values:
                
                if hasattr(self, 'ureceptr_df'):
                    pass
                    
                       
                else:
                    messagebox.showinfo( "Missing user receptors", "Please upload a user receptors file.")
                
            elif True not in user_rec_check.values:
              
                self.ureceptr_df = None 
                
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
                
                   
            if hasattr(self, 'multipoly_df') and hasattr(self, 'ureceptr_df') and hasattr(self, 'multibuoy_df'):
                self.ready = True
                print("Ready to run!")
            
        
       #%%if the object is ready
                if self.ready == True:
                   
                    #tell user to check the Progress/Log section
                   
                    
                   
                   
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
                        
                       #save version of this gui as is? constantly overwrite it once each facility is done?
                        start = time.time()
                        
                        the_queue.put("\nRunning facility " + str(num) + " of " + str(len(fac_list)))
                        
                        facid = fac
                        
                        result = pass_ob.prep_facility(facid)
                        
                        the_queue.put("Building Runstream File for " + str(facid))
        
                        result.build()
                      
                        #create fac folder
                        fac_folder = "output/"+ str(facid) + "/"
                        if os.path.exists(fac_folder):
                            pass
                        else:
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
                            
                            #create facility kml
                            the_queue.put("Writing KML file for " + str(facid))
                            facility_kml = fkml.facility_kml(facid, result.cenlat, result.cenlon, fac_folder) 
                            
                            pace =  str(time.time()-start) + 'seconds'
                            
                            the_queue.put("Finished calculations for " + str(facid) + ' after' + pace + "\n")
                        
                        
                        #increment facility count
                            num += 1 
                            
                            
              
                the_queue.put("\nFinished running all facilities.\n")
                
                #reset all inputs if everything finished
                self.fac_list.set('')
                self.faclist_df = self.faclist_df.empty
                print(self.faclist_df)
                       
                self.hap_list.set('')
                self.hapemis_df = self.hapemis_df.empty
                print(self.hapemis_df)
                
                self.emisloc_list.set('')
                self.emisloc_df = self.emisloc_df.empty
                print(self.emisloc_df)
                
                if hasattr(self, 'u_receptors'):
                    self.u_receptors.set(False)
                    self.urep.destroy()
                    self.urep_list_man.destroy()
                    
                self.running = False
                
        
        
        
#%% Create Thread for Threaded Process   
    def runThread(self):
        global instruction_instance
        instruction_instance.set("Hem4 Running, check the log tab for updates")
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
            self.scr.configure(state='normal')
            self.scr.insert(tk.INSERT, message)
            self.scr.insert(tk.INSERT, "\n")
            self.scr.configure(state='disabled')
            hem4.win.after(25, self.after_callback)   
         
        
        

#%% Start GUI

the_queue = queue.Queue()


hem4 = Hem4()
hem4.win.after(25, hem4.after_callback)
hem4.win.mainloop()
