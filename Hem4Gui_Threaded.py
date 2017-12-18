# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 10:26:13 2017

@author: jbaker
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
    
        #maybe add a tooltip?
    
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
        tabControl = ttk.Notebook(self.win)     # Create Tab Control

        tab1 = ttk.Frame(tabControl)            # Create a tab
        tabControl.add(tab1, text='HEM4')      # Add the tab

        tab2 = ttk.Frame(tabControl)            # Add a second tab
        tabControl.add(tab2, text='Log')      # Make second tab visible

        tabControl.pack(expand=1, fill="both")  # Pack to make visible
        
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
        self.s9 = tk.Frame(self.main, width=250, height=200)
        self.s10 = tk.Frame(self.main, width=250, height=200)

        self.s1.grid(row=0)
        self.s2.grid(row=1, column=0, sticky="nsew")
        self.s3.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.s4.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.s5.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.s6.grid(row=5, column=0, columnspan=2, sticky="nsew")
        self.s7.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.s8.grid(row=7, column=0, sticky="nsew")
        self.s9.grid(row=8, column=0, sticky="nsew")
        self.s10.grid(row=9, column=0, sticky="nsew")

        self.main.grid_rowconfigure(10, weight=1)
        self.main.grid_columnconfigure(2, weight=1)
        self.s2.grid_propagate(0)
        #self.s1.grid_propagate(0)
    
        # create container frame to hold log
        self.log = ttk.LabelFrame(tab2, text=' Hem4 Progress Log ')
        self.log.grid(column=0, row=0)
        # Adding a Textbox Entry widget
        scrolW  = 30; scrolH  =  3
        self.scr = scrolledtext.ScrolledText(self.log, width=scrolW, height=scrolH, wrap=tk.WORD)
        self.scr.grid(column=0, row=3, sticky='WE', columnspan=3)
        
#%% Set Quit and Run buttons        
        self.quit = tk.Button(self.s10, text="QUIT", fg="red",
                              command=self.quit_gui)
        self.quit.grid(row=0, column=2, sticky="E")
        
        #run only appears once the required files have been set
        self.run_button = tk.Button(self.s10, text='RUN', fg="green", command=self.runThread).grid(row=0, column=1)
        
#%% Setting up  directions text space
        #Instructions title
        #instructions = tk.Label(self.s2, text = "Instructions:", padx=80)
        #instructions.grid(row = 0, sticky="W")

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
        self.fac_up = ttk.Button(self.s3)
        self.fac_up["text"] = "Browse"
        self.fac_up["command"] = self.upload_fac
        self.fac_up.grid(row=2, column=0, sticky="W")
        self.fac_up.bind('<Enter>', lambda e:self.fac_browse())
       
        
        
        #facilities text entry
        self.fac_list = tk.StringVar(self.s3)
        self.fac_list_man = ttk.Entry(self.s3)
        self.fac_list_man["width"] = 55
        self.fac_list_man["textvariable"]= self.fac_list
        self.fac_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.fac_list_man.bind('<Button-1>', lambda e:self.fac_man())
        
        
        
        #Hap emissions label
        hap_label = tk.Label(self.s4, font="-size 10",  text="Please select a HAP Emissions file(required):                                                  ")
        hap_label.grid(row=1, sticky="W")
        
        #hap emissions upload button
        self.hap_up = ttk.Button(self.s4)
        self.hap_up["text"] = "Browse"
        self.hap_up["command"] = self.upload_hap
        self.hap_up.grid(row=2, column=0, sticky='W')
        #event handler for instructions (Button 1 is the left mouse click)
        self.hap_up.bind('<Enter>', lambda e:self.hap_browse())
        
        
        #hap emission text entry
        self.hap_list = tk.StringVar(self.s4)
        self.hap_list_man = ttk.Entry(self.s4)
        self.hap_list_man["width"] = 55
        self.hap_list_man["textvariable"]= self.hap_list
        self.hap_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.hap_list_man.bind('<Button-1>', lambda e:self.hap_man())
        
        
        #Emissions location label
        emisloc_label = tk.Label(self.s5, font="-size 10",  text="Please select an Emissions Locations file(required):                                         ")
        emisloc_label.grid(row=1, sticky="W")
        
        #emissions location upload button
        self.emisloc_up = ttk.Button(self.s5)
        self.emisloc_up["text"] = "Browse"
        self.emisloc_up["command"] = self.upload_emisloc
        self.emisloc_up.grid(row=2, column=0, sticky='W')
        #event handler for instructions (Button 1 is the left mouse click)
        self.emisloc_up.bind('<Enter>', lambda e:self.emisloc_browse())
      
        #emission loccation file text entry
        self.emisloc_list = tk.StringVar(self.s5)
        self.emisloc_list_man = ttk.Entry(self.s5)
        self.emisloc_list_man["width"] = 55
        self.emisloc_list_man["textvariable"]= self.emisloc_list
        self.emisloc_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.emisloc_list_man.bind('<Button-1>', lambda e:self.emisloc_man())
        
        
        #Polygon sources label
        poly_label = tk.Label(self.s6, font="-size 10",  text="Please select a Polygon Vertex file (if included):")
        poly_label.grid(row=1, sticky="W")
        
        #polygon sources upload button
        self.poly_up = ttk.Button(self.s6)
        self.poly_up["text"] = "Browse"
        self.poly_up["command"] = self.upload_poly
        self.poly_up.grid(row=2, column=0, sticky="W")
        #event handler for instructions (Button 1 is the left mouse click)
        self.poly_up.bind('<Enter>', lambda e:self.poly_browse())
       
        #polygon sources loccation file text entry
        self.poly_list = tk.StringVar(self.s6)
        self.poly_list_man = ttk.Entry(self.s6)
        self.poly_list_man["width"] = 55
        self.poly_list_man["textvariable"]= self.poly_list
        self.poly_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.poly_list_man.bind('<Button-1>', lambda e:self.poly_man())
        
        
        #Buoyant Line  label
        bouyant_label = tk.Label(self.s7, font="-size 10",  text="Please select a Bouyant Line Source Parameter file (if included):")
        bouyant_label.grid(row=1, sticky="W")
        
        #bouyant line file upload button
        self.bouyant_up = ttk.Button(self.s7)
        self.bouyant_up["text"] = "Browse"
        self.bouyant_up["command"] = self.upload_bouyant
        self.bouyant_up.grid(row=2, column=0, sticky='W')
        #event handler for instructions (Button 1 is the left mouse click)
        self.bouyant_up.bind('<Enter>', lambda e:self.bouyant_browse())
        
        
        #bouyant line file text entry
        self.bouyant_list = tk.StringVar(self.s7)
        self.bouyant_list_man = ttk.Entry(self.s7)
        self.bouyant_list_man["width"] = 55
        self.bouyant_list_man["textvariable"]= self.bouyant_list
        self.bouyant_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.bouyant_list_man.bind('<Button-1>', lambda e:self.bouyant_man())
        
        
        #census year label
        #self.census_label = tk.Label(self.s8, text="Select the census year used for modeling:")
        #self.census_label.grid(row=1, column=0, sticky="W")
        
        #census year 2000
        #self.twok = tk.BooleanVar()
        #self.twok.set(False)
        #self.census_2000 = ttk.Checkbutton(self.s8, text="2000", variable=self.twok, command=self.census_sel).grid(row=1, column=1)
        
        #census year 2010
        #self.twok10 = tk.BooleanVar()
        #self.twok10.set(False)
        #self.census_2010 = ttk.Checkbutton(self.s8, text="2010", variable=self.twok10, command=self.census_sel).grid(row=1, column=2)
        
        
        #csv output label
        self.csv_label = tk.Label(self.s8, font="-size 10",  text="Select to output DBF files in CSV format")
        self.csv_label.grid(row=2, column=0, sticky="W")
        
        #csv output
        self.csv= tk.BooleanVar()
        self.csv.set(False)
        self.csv_output = ttk.Checkbutton(self.s8, variable=self.csv, command=self.csv_sel).grid(row=2, column=1, sticky="w")
        
        
        #optional input labels
        self.optional_label = tk.Label(self.s9, font="-size 10",  text="OPTIONAL Input Files", pady=10)
        self.optional_label.grid(row=0, column=1, sticky="W")
        
        #user receptors
        #self.receptors_label = tk.Label(self.s9, text="Include user receptors for facilities, as indicated in the Facilities List Options file.").grid(row=1)
        self.u_receptors= tk.BooleanVar()
        self.u_receptors.set(False)
        self.ur_op = ttk.Checkbutton(self.s9, text="Include user receptors for any facilities, as indicated in the Facilities List Options file?", variable=self.u_receptors, command=self.add_ur).grid(row=1, column=1, sticky="w")
        
        #building downwash
        self.building= tk.BooleanVar()
        self.building.set(False)
        self.downwash_op = ttk.Checkbutton(self.s9, text="Include building downwash for any facilities, as indicated in the Facilities List Options file.?", variable=self.building, command=self.add_downwash).grid(row=3, column=1, sticky="w")
        
        #deposition/depletion
        self.depdep= tk.BooleanVar()
        self.depdep.set(False)
        self.dep_op = ttk.Checkbutton(self.s9,  text="Include deposition or depletion for any facilities, as indicated in the Facilities List Options file.?", variable=self.depdep).grid(row=5, column=1, sticky="W")
        
        #%% Specific upload functions for selecting each file, once selected convert excel file to dataframe
   
    #handle upload for facilities file
    def upload_fac(self):
       #get file name from open dialogue
        filename = askopenfilename()
        #if the upload is canceled 
        if not filename:
            messagebox.showinfo("Required Input Missing", "A facilities option file is required to run HEM4.")
        elif is_excel(filename) == False:
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for facility options.")
        elif is_excel(filename) == True:
            file_path = os.path.abspath(filename)
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
        
        
            #print(self.faclist_df)
            
    #%%handle upload for hap emissions file
    def upload_hap(self):
       #get file name from open dialogue
        filename = askopenfilename()
        #if the upload is canceled 
        if not filename:
            messagebox.showinfo("Required Input Missing", "A hap emissions file is required to run HEM4.") 
        elif is_excel(filename) == False:
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for hap emissions.")
        elif is_excel(filename) == True:
            file_path = os.path.abspath(filename)
            self.hap_list.set(file_path)
            self.hap_path = file_path
            
            #HAP EMISSIONS excel to dataframe    
            self.hapemis_df = pd.read_excel(open(self.hap_path, "rb")
                , names=("fac_id","source_id","pollutant","emis_tpy","part_frac")
                , converters={"fac_id":str,"source_id":str,"pollutant":str,"emis_tpy":float,"part_frac":float})
            
            
            
            
    # %%handle upload for emissions location file
    def upload_emisloc(self):
       #get file name from open dialogue
        filename = askopenfilename()
        #if the upload is canceled 
        if filename == None:
            messagebox.showinfo("Required Input Missing", "An emissions locations file is required to run HEM4.") 
        elif is_excel(filename) == False:
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for emissions locations.")
        elif is_excel(filename) == True:
            file_path = os.path.abspath(filename)
            self.emisloc_list.set(file_path)
            self.emisloc_path = file_path
            #print(file_path)
            
            #EMISSIONS LOCATION excel to dataframe

            self.emisloc_df = pd.read_excel(open(self.emisloc_path, "rb")
                  , names=("fac_id","source_id","location_type","lon","lat","utmzone","source_type"
                           ,"lengthx","lengthy","angle","horzdim","vertdim","areavolrelhgt","stkht"
                           ,"stkdia","stkvel","stktemp","elev","x2","y2")
                  , converters={"fac_id":str,"source_id":str,"location_type":str,"lon":float,"lat":float
                  ,"utmzone":float,"source_type":str,"lengthx":float,"lengthy":float,"angle":float
                  ,"horzdim":float,"vertdim":float,"areavolrelhgt":float,"stkht":float,"stkdia":float
                  ,"stkvel":float,"stktemp":float,"elev":float,"x2":float,"y2":float})
                
            
    #%%handle upload for polygon sources file
    def upload_poly(self):
        if hasattr(self, "emisloc_df"): 
            filename = askopenfilename()
        else:
            messagebox.showinfo("Emissions Locations File Missing", "Please upload an Emissions Locations file before adding a Polyvertex file.")
        
        #if the upload is canceled 
        if filename == None:
            print("Canceled!")
            
        elif is_excel(filename) == False:
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for polygon sources.")
        elif is_excel(filename) == True:
            file_path = os.path.abspath(filename)
            self.poly_list.set(file_path)
            self.poly_path = file_path
            
            #POLYVERTEX excel to dataframe
            self.multipoly_df = pd.read_excel(open(self.poly_path, "rb")
                  , names=("fac_id","source_id","location_type","lon","lat","utmzone"
                           ,"numvert","area")
                  , converters={"fac_id":str,"source_id":str,"location_type":str,"lon":float
                                ,"lat":float,"utmzone":str,"numvert":float,"area":float})
            
    
    
    
            #get polyvertex facility list
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
            
    #%%handle upload for buoyant line file
    def upload_bouyant(self):
        
        if hasattr(self, "emisloc_df"): 
            filename = askopenfilename()
        else:
            messagebox.showinfo("Emissions Locations File Missing", "Please upload an Emissions Locations file before adding a Bouyant line file.")
        
        #if the upload is canceled 
        if filename == None:
            print("Canceled!")
           
        elif is_excel(filename) == False:
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for bouyant line.")
        elif is_excel(filename) == True:
            file_path = os.path.abspath(filename)
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
            
      #%%handle user receptors
    def upload_urep(self):
         #get file name from open dialogue
        if hasattr(self, "faclist_df"): 
            filename = askopenfilename()
        else:
            messagebox.showinfo("Facilities List Option File Missing", "Please upload a Facilities List Options file before selecting a User Receptors file.")
            
        #if the upload is canceled 
        if filename == None:
           pass 
        elif is_excel(filename) == False:
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for user receptors.")
        elif is_excel(filename) == True:
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
            
        
    #%% handle building downwash    
    def upload_bd(self):
         #get file name from open dialogue
        filename = askopenfilename()
        #if the upload is canceled 
        if filename == None:
            print("Canceled!")
            #eventually open box or some notification to say this is required 
        elif is_excel(filename) == False:
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for building downwash.")
        elif is_excel(filename) == True:
            file_path = os.path.abspath(filename)
            self.bd_list.set(file_path)
            self.bd_path = file_path     
        
 #%% Event handlers for porting instructions

    #reset instructions space
    def reset_instructions(self):
        global instruction_instance
        instruction_instance.set(" ")

    #facilities instructions
    def fac_browse(self):
        global instruction_instance
        read_inst = open("instructions/fac_browse.txt", 'r')
        instruction_instance.set(read_inst.read())
  
    def fac_man(self):
        global instruction_instance
        read_inst = open("instructions/fac_man.txt", 'r')
        instruction_instance.set(read_inst.read())

    #hap emissions instructions
    def hap_browse(self):
        global instruction_instance
        read_inst = open("instructions/hap_browse.txt", 'r')
        instruction_instance.set(read_inst.read())
   
    def hap_man(self):
        global instruction_instance
        read_inst = open("instructions/hap_man.txt", 'r')
        instruction_instance.set(read_inst.read())
    
    
    #emissions location instructions    
    def emisloc_browse(self):
        global instruction_instance
        read_inst = open("instructions/emis_browse.txt", 'r')
        instruction_instance.set(read_inst.read())
   
    def emisloc_man(self):
        global instruction_instance
        read_inst = open("instructions/emis_man.txt", 'r')
        instruction_instance.set(read_inst.read())

                
      #poly vertex location instructions    
    def poly_browse(self):
        global instruction_instance
        read_inst = open("instructions/poly_inst.txt", 'r')
        instruction_instance.set(read_inst.read())
   
    def poly_man(self):
        global instruction_instance
        read_inst = open("instructions/poly_inst.txt", 'r')
        instruction_instance.set(read_inst.read())      
    
    #bouyant line instructions    
    def bouyant_browse(self):
        global instruction_instance
        read_inst = open("instructions/bouyant_inst.txt", 'r')
        instruction_instance.set(read_inst.read())
   
    def bouyant_man(self):
        global instruction_instance
        read_inst = open("instructions/bouyant_inst.txt", 'r')
        instruction_instance.set(read_inst.read()) 
  
    #census list instructions should new census data become available
    #def census_sel(self):
        #global instruction_instance
        #read_inst = open("instructions/census_inst.txt", 'r')
        #instruction_instance.set(read_inst.read())
        
        
        #if self.twok.get() == True:
           # print("2000")
           # self.twok10.set(False)
           # self.census = "2000"
            
        #elif self.twok10.get() == True:
         #   print("2010")
         #   self.twok.set(False)
         #   self.census = "2010"
            
            

    #csv option instructions
    def csv_sel(self):
        global instruction_instance
        read_inst = open("instructions/csv_inst.txt", 'r')
        instruction_instance.set(read_inst.read())
        
    
            
    #user receptor instructions
    def urep_browse(self):
        global instruction_instance
        #read_inst = open("instructions/fac_browse.txt", 'r')
        #instruction_instance.set(read_inst.read())
  
    def urep_man(self):
        global instruction_instance
        #read_inst = open("instructions/fac_man.txt", 'r')
        #instruction_instance.set(read_inst.read())        
            
    #building downwash instructions
    def bd_browse(self):
        global instruction_instance
        #read_inst = open("instructions/fac_browse.txt", 'r')
        #instruction_instance.set(read_inst.read())
  
    def bd_man(self):
        global instruction_instance
        #read_inst = open("instructions/fac_man.txt", 'r')
        #instruction_instance.set(read_inst.read())        
        
        
        
  #%% Dynamic inputs for adding options

    def add_downwash(self):
        
        #when box is checked add row with input
        if self.building.get() == True:
            
            #user recptors upload button
            self.bd = ttk.Button(self.s9)
            self.bd["text"] = "Browse"
            self.bd["command"] = self.upload_bd
            self.bd.grid(row=4, column=1, sticky="W")
            self.bd.bind('<Enter>', lambda e:self.bd_browse())
            
            #user receptor text entry
            self.bd_list = tk.StringVar(self.s9)
            self.bd_list_man = ttk.Entry(self.s9)
            self.bd_list_man["width"] = 55
            self.bd_list_man["textvariable"]= self.bd_list
            self.bd_list_man.grid(row=4, column=1, sticky='E', padx =10)
            #event handler for instructions (Button 1 is the left mouse click)
            self.bd_list_man.bind('<Button-1>', lambda e:self.bd_man())
            
            
        if self.building.get() == False:
            self.bd.destroy()
            self.bd_list_man.destroy()
            

    def add_ur(self):
        #when box is checked add row with input
        if self.u_receptors.get() == True:
            
            #user recptors upload button
            self.urep = ttk.Button(self.s9)
            self.urep["text"] = "Browse"
            self.urep["command"] = self.upload_urep
            self.urep.grid(row=2, column=1, sticky="W", padx=10)
            self.urep.bind('<Enter>', lambda e:self.urep_browse())
            
            #user receptor text entry
            self.urep_list = tk.StringVar(self.s9)
            self.urep_list_man = ttk.Entry(self.s9)
            self.urep_list_man["width"] = 55
            self.urep_list_man["textvariable"]= self.urep_list
            self.urep_list_man.grid(row=2, column=1, sticky='E', padx=85)
            #event handler for instructions (Button 1 is the left mouse click)
            self.urep_list_man.bind('<Button-1>', lambda e:self.urep_man())
            
            
        if self.u_receptors.get() == False:
            self.urep.destroy()
            self.urep_list_man.destroy()

          


#%% Run function with checks if somethign is missing raise the error here and create an additional dialogue before trying to run the file

    def run(self):
        
# check file dataframes
        
        ready = False
        
        #make sure fac_list df was created correctly
        if hasattr(self, "faclist_df"):
            
            if self.faclist_df.empty:
                messagebox.showinfo("Error","There was an error uploading Facilities List Option File, please try again")
                ready = False
            else:
                ready = True
        else:
            ready = False
            messagebox.showinfo("Error","There was an error uploading Facilities List Option File, please try again")
       
        #make sure emis_loc df was created correctly
        if hasattr(self, "emisloc_df"):
            
            if self.emisloc_df.empty:
                messagebox.showinfo("Error","There was an error uploading Emissions Locations File, please try again")
                ready = False
            else:
                ready = True
        else:
            ready = False
            messagebox.showinfo("Error","There was an error uploading Emissions Locations File, please try again")

       #make sure hap_emis  df was created correctly
        if hasattr(self, "hapemis_df"):
            
            if self.hapemis_df.empty:
                messagebox.showinfo("Error","There was an error uploading HAP Emissions File, please try again")
                ready = False
            else:
                ready = True
        else:
            ready = False
            messagebox.showinfo("Error","There was an error uploading HAP Emissions File, please try again")
        
        
        
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
        if self.depdep ==True:
            print("Include depletion calculation")
        else:
            self.depdep = None
        
        #if they want output as csv 
        if self.csv == True:
            print("Output in CSV as well")
        else:
            self.csv == False
     
        
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
        
        
       #%%if the object is ready
        if ready == True:
           
            #tell user to check the Progress/Log section
           
            
           #save version of this gui as is? constantly overwrite it once each facility is done?
           
           
           messagebox.askokcancel("Confirm HEM4 Run", "Clicking 'OK' will start HEM4.")
           
           #create object for prepare inputs
           self.running = True
           #create a Google Earth KML of all sources to be modeled
           createkml = cmk.multi_kml(self.emisloc_df, self.multipoly_df, self.multibuoy_df)
           source_map = createkml.create_sourcemap()
           kmlfiles = createkml.write_kml_emis_loc(source_map)


           pass_ob = prepare.Prepare_Inputs( self.faclist_df, self.emisloc_df, self.hapemis_df, self.multipoly_df, self.multibuoy_df, self.ureceptr_df)
           the_queue.put(pass_ob.message)
           

    # let's tell after_callback that this completed
           #print('thread_target puts None to the queue')
          
           the_queue.put(pass_ob.message)
           prep = pass_ob.run_facilities()
           
           
      
            
           self.running = False
        
        
#%% Create Thread for Threaded Process   
    def runThread(self):
        global instruction_instance
        instruction_instance.set("Hem-4 Running, check the progress/log tab for updates")
        runT = Thread(target=self.run)
        runT.daemon = True
        runT.start()
        
        
    def after_callback(self):
        try:
            message = the_queue.get(block=False)
        except queue.Empty:
            # let's try again later
            hem4.win.after(50, self.after_callback)
            return

        print('after_callback got', message)
        if message is not None:
            # we're not done yet, let's do something with the message and
            # come back ater
            #tk.label['text'] = message
            hem4.win.after(50, self.after_callback)   
         
        
        

#%% Start GUI

the_queue = queue.Queue()


hem4 = Hem4()
hem4.win.after(50, hem4.after_callback)
hem4.win.mainloop()
