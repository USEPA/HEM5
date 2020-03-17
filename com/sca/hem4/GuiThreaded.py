# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 10:26:13 2017

@author: dlindsey
"""
import os
import queue
import sys
import tkinter as tk
import tkinter.ttk as ttk

from concurrent.futures import ThreadPoolExecutor
from threading import Event
from tkinter import messagebox
from tkinter import scrolledtext
import numpy as np

import datetime
from com.sca.hem4.Processor import Processor
from com.sca.hem4.log.Logger import Logger
from com.sca.hem4.tools.CensusUpdater import CensusUpdater
from com.sca.hem4.model.Model import Model
from com.sca.hem4.upload.FileUploader import FileUploader
from tkinter.filedialog import askopenfilename
from com.sca.hem4.checker.InputChecker import InputChecker
from com.sca.hem4.DepositionDepletion import check_dep, check_phase
from com.sca.hem4.SaveState import SaveState
from tkinter.simpledialog import Dialog, Toplevel
from ttkthemes import ThemedStyle

from collections import defaultdict


TITLE_FONT= ("Verdana", 14)
TEXT_FONT = ("Verdana", 10)
LOG_FONT = ("Verdana", 12)

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()
#%% HEM4 GUI



class Hem4(tk.Frame):

    def __init__ (self, container, messageQueue, callbackQueue, *args, **kwargs):
        Page.__init__(self, master=container, *args, **kwargs)
        """
        The HEM4 class object builds the GUI for the HEM4 application.
        """
        
#        self.s=ttk.Style()
#        print(self.s.theme_names())
#        self.s.theme_use('clam')

        # Set an environment variable needed for a HEM4 distribution
        if getattr(sys, 'frozen', False):
            os.environ['PROJ_LIB'] = os.path.join(os.path.split(__file__)[0], 'pyproj')
        else :
            pass                
        
        self.running = False
        self.aborted = False
        self.ready = False

        # Create the model
        self.model = Model()

        # Create a file uploader
        self.uploader = FileUploader(self.model)
        self.messageQueue = messageQueue
        
        # Upload the Dose response and Target Organ Endponts libraries
        self.uploader.uploadLibrary("haplib")
        self.uploader.uploadLibrary("organs")

        # The callback queue is shared by the main thread and the processing thread.
        # The main thread polls it periodically (via the tkinter event loop) to see
        # if the processing thread has completed.
        self.callbackQueue = callbackQueue
        self.processor = None
        self.lastException = None

        self.run_button = None
        self.fac_up = None
        self.hap_up = None
        self.emisloc_up = None
        self.urep = None
        self.urepaltButton = None
        self.poly_up = None
        self.buoyant_up = None
        self.bldgdw_up = None
        self.dep_part_up = None
        self.dep_land_up = None
        self.dep_seasons_up = None
        
        #status for working with optional inputs
        self.optionaltab = False
        self.hiddenoptab = False
        
        self.deptab = False
        self.hiddendeptab = False

        self.createWidgets()
        
        self.after(25, self.after_callback)
        self.after(500, self.check_processing)

        Logger.messageQueue = messageQueue


    def close(self):
        Logger.close(True)

#%% Quit Function    
    def quit_app(self):
        """
        Function handles quiting HEM4 by closing the window containing
        the GUI and exiting all background processes & threads
        """
        if self.running:
            override = messagebox.askokcancel("Confirm HEM4 Quit", "Are you "+
                                              "sure? HEM4 is currently running. Clicking 'OK' will stop HEM4.")

            if override:
                # Abort the thread and wait for it to stop...once it has
                # completed, it will signal this class to kill the GUI
                Logger.logMessage("Stopping HEM4...")
                self.processor.abortProcessing()
                self.aborted = True
                self.display_app_quit()

        else:
            # If we're not running, the only thing to do is reset the GUI...
            self.reset_gui()
            Logger.logMessage("HEM4 stopped")
            

    def display_app_quit(self):
        self.enable_widgets(self.main, False)

        message = "HEM4 is stopping. Please wait."
        tk.Label(self, text=message, font=TEXT_FONT, bg="palegreen3").pack()

    def disable_buttons(self):
        self.enable_widgets(self.run_button, False)
        self.enable_widgets(self.fac_up, False)
        self.enable_widgets(self.hap_up, False)
        self.enable_widgets(self.emisloc_up, False)

        if self.urep is not None:
            self.enable_widgets(self.urep, False)
        if self.urepaltButton is not None:
            self.enable_widgets(self.urepaltButton, False)
        if self.poly_up is not None:
            self.enable_widgets(self.poly_up, False)
        if self.buoyant_up is not None:
            self.enable_widgets(self.buoyant_up, False)
        if self.bldgdw_up is not None:
            self.enable_widgets(self.bldgdw_up, False)
        if self.dep_part_up is not None:
            self.enable_widgets(self.dep_part_up, False)
        if self.dep_land_up is not None:
            self.enable_widgets(self.dep_land_up, False)
        if self.dep_seasons_up is not None:
            self.enable_widgets(self.dep_seasons_up, False)

    def enable_buttons(self):
        self.enable_widgets(self.run_button, True)
        self.enable_widgets(self.fac_up, True)
        self.enable_widgets(self.hap_up, True)
        self.enable_widgets(self.emisloc_up, True)

        if self.urep is not None:
            self.enable_widgets(self.urep, True)
        if self.urepaltButton is not None:
            self.enable_widgets(self.urepaltButton, True)
        if self.poly_up is not None:
            self.enable_widgets(self.poly_up, True)
        if self.buoyant_up is not None:
            self.enable_widgets(self.buoyant_up, True)
        if self.bldgdw_up is not None:
            self.enable_widgets(self.bldgdw_up, True)
        if self.dep_part_up is not None:
            self.enable_widgets(self.dep_part_up, True)
        if self.dep_land_up is not None:
            self.enable_widgets(self.dep_land_up, True)
        if self.dep_seasons_up is not None:
            self.enable_widgets(self.dep_seasons_up, True)
            
    def enable_widgets(self, root, enabled):
        """
        Recursively disable widgets starting from the given root.
        """
        if not root.winfo_exists():
            return

        state = 'normal' if enabled else 'disabled'
        if "state" in root.keys():
            root.configure(state=state)

        for child in root.winfo_children():
            self.enable_widgets(child, enabled)

    def quit_gui(self):
        """
        Destroy the GUI, close the log, and exit. The latter two are OK here, because
        we don't ever destroy the GUI until all processing has stopped, which means
        it's -really- time to end!
        """
#        self.quit()
#        self.destroy()
#        self.close()
#        sys.exit()

    def reset_gui(self):
        #reset all inputs if everything finished. actually destroy and recreate all inputs
        self.model.reset()

        self.fac_list.set('')
        self.hap_list.set('')
        self.emisloc_list.set('')
        self.group_list.set('')

        self.check_altrec.set(False)
        self.set_altrec()

        if hasattr(self, 's6'):
            self.urep.destroy()
            self.urep_list_man.destroy()
            self.ur_label.destroy()
            self.s6.destroy()
            
        if hasattr(self, "optionalinputtab"):

            if hasattr(self, 's7'):
                self.buoyant_list_man.destroy()
                self.buoyant_up.destroy()
                self.b_label.destroy()
                self.s7.destroy()
    
            if hasattr(self, 's8'):
                self.poly_list_man.destroy()
                self.poly_up.destroy()
                self.poly_label.destroy()
                self.s8.destroy()
    
            if hasattr(self, 's9'):
                self.bldgdw_up.destroy()
                self.bldgdw_list_man.destroy()
                self.bldgdw_label.destroy()
                self.s9.destroy()
                
            
            self.tabControl.hide(self.optionalinputtab)
            self.hiddenoptab = True
            
            
        if hasattr(self, "depinputtab"): 

            #clear particle
            if hasattr(self, 'dep_part'):
                self.dep_part_up.destroy()
                self.dep_part_man.destroy()
                self.dep_part.set('')
#                self.dep_part.destroy()
                self.s10.destroy()
                
                
            #clear land
            if hasattr(self, 'dep_land'):
                self.dep_land_up.destroy()
                self.dep_land_man.destroy()
                self.dep_land.set('')
#                self.dep_land.destroy()
                self.s11.destroy()
                

            #clear vegetation
            if hasattr(self, 'dep_veg'):
                self.dep_veg_up.destroy()
                self.dep_veg_man.destroy()
                self.dep_veg.set('')
#                self.dep_veg.destroy()
                self.s12.destroy()
            
            self.tabControl.hide(self.depinputtab)
            self.hiddendeptab = True
              
              
            
            
            
        #destroy stop
        if hasattr(self, 'stop'):
            self.stop.destroy()
        
        #add start button
        self.run_button = tk.Button(self.main, text='RUN', fg="green", bg='lightgrey', relief='solid', borderwidth=2,
                                    command=self.run, font=TEXT_FONT)
        self.run_button.grid(row=10, column=0, sticky="E", padx=5, pady=5)
        
        global instruction_instance
        self.instruction_instance.set(" ")

        self.after(100, self.enable_buttons)

#%% Open HEM4 User Guide
    def user_guide(self):
        """ 
        Function opens the user guide for Hem4
        *** needs new HEM4 pdf ***
        """
        
        os.startfile("userguide\Multi_HEM-3_Users_Guide.pdf")
    
                
#%%Create Widgets

    def update_census(self):
        """
        Function creates thread for running HEM4 concurrently with tkinter GUI
        """
        executor = ThreadPoolExecutor(max_workers=1)

        self.processor = Processor(self.model, Event())
        future = executor.submit(self.censusupdater.update, self.censusUpdatePath)
        future.add_done_callback(self.update_census_finish)

    def update_census_finish(self, future):
        self.callbackQueue.put(self.finish_census_update)

    def finish_census_update(self):
        self.cu_list.set("")

    def uploadCensusUpdates(self):
        self.censusupdater = CensusUpdater()
        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.censusUpdatePath = fullpath
            self.cu_list.set(fullpath)
            
    def add_instructions(self, placeholder1, placeholder2):
        
        #Dynamic instructions place holder
        global instruction_instance
        self.instruction_instance = tk.StringVar(placeholder1)
        self.instruction_instance.set(" ")
        self.dynamic_inst = tk.Label(placeholder2, wraplength=600, font=TEXT_FONT, pady=5, bg='palegreen3') 
        self.dynamic_inst.config(height=4)
        
        self.dynamic_inst["textvariable"] = self.instruction_instance 
        self.dynamic_inst.grid(row=1, column=0)
        
        
    def add_optional_instructions(self, placeholder):
        """
        Function adds a dynamic instructions instance to optional input tab
        
        """
        
        if hasattr(self, "optionalinputtab"):
            
            self.optional_inst = tk.Label(placeholder, wraplength=600, font=TEXT_FONT, pady=5, bg='palegreen3') 
            self.optional_inst.config(height=4)
        
            self.optional_inst["textvariable"] = self.instruction_instance 
            self.optional_inst.grid(row=1, column=0)
        
        if hasattr(self, "depinputtab"):
            self.dep_inst = tk.Label(placeholder, wraplength=600, font=TEXT_FONT, pady=5, bg='palegreen3') 
            self.dep_inst.config(height=4)
        
            self.dep_inst["textvariable"] = self.instruction_instance 
            self.dep_inst.grid(row=1, column=0)
            
    def backtomenu(self):
        self.lower()
        self.reset_gui()
    
    
        

    def createWidgets(self):
        """
        Function creates the main tab structure and required inputs,
        referred to as widgets in tkinter.
        
        To create widgets, the widget must be assigned to a variable and then 
        placed on a grid or within a 'frame'.
        """
        
        self.noteStyler = ttk.Style()
        self.noteStyler.configure("TNotebook", background="palegreen3", borderwidth=0)
        self.noteStyler.configure("TNotebook.Tab", background="palegreen3", borderwidth=0)
        self.noteStyler.configure("TFrame", background="palegreen3", borderwidth=0)

        
        # Tab Control introduced here --------------------------------------
        self.tabControl = ttk.Notebook(self, style='TNotebook')     # Create Tab Control

        if hasattr('self', 'main'):
            if self.main is None:
                self.main = tk.Frame(self.tabControl, bg='palegreen3')            # Create a tab
                self.tabControl.add(self.main, text='HEM4')
                
        else:
            
            self.main = tk.Frame(self.tabControl, bg='palegreen3')            # Create a tab
            self.tabControl.add(self.main, text='HEM4')      # Add the tab

        self.tab2 = tk.Frame(self.tabControl, bg='palegreen3')            # Add a second tab
        self.tabControl.add(self.tab2, text='Log')      # Make second tab visible



        tab3 = tk.Frame(self.tabControl, bg='palegreen3')            # Add a third tab
        self.tabControl.add(tab3, text='Census')      # Make third tab visible

        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible

        # Create container frame to hold census update stuff
        self.censusupdates = ttk.LabelFrame(tab3, text='Census updates',
                                   labelanchor="n")
        self.censusupdates.grid(column=0, row=1)

        #create discreet sections for GUI in tab3
        self.cu1 = tk.Frame(self.censusupdates, width=1000, height=200, background="palegreen3")
        self.cu1.grid(row=0)

        # census update label
        cu_label = tk.Label(self.cu1, font=TEXT_FONT, bg="palegreen3",
                             text="Please select a census update file:")
        cu_label.grid(row=1, sticky="W")

        # census update upload button
        self.cu_up = tk.Button(self.cu1, bg='lightgrey', relief='solid', borderwidth=2,
                                 command = lambda: self.uploadCensusUpdates())
        self.cu_up["text"] = "Browse"
        self.cu_up.grid(row=2, column=0, sticky="W")

        # census update text entry
        self.cu_list = tk.StringVar(self.cu1)
        self.cu_list_man = ttk.Entry(self.cu1)
        self.cu_list_man["width"] = 100
        self.cu_list_man["textvariable"]= self.cu_list
        self.cu_list_man.grid(row=2, column=0, sticky='E', padx=85)

        self.cu_update = tk.Button(self.cu1, text="UPDATE", fg="green", bg='lightgrey', relief='solid', borderwidth=2,
                              command=self.update_census)
        self.cu_update.grid(row=3, column=0, sticky="W", padx=85, pady=20)

        #create discreet sections for GUI in tab1
        self.s1 = tk.Frame(self.main, width=750, height=50, bg="palegreen3")
        self.s2 = tk.Frame(self.main, width=1000, height=50, bg="palegreen3")
        self.s3 = tk.Frame(self.main, width=750, height=50, bg="palegreen3", pady=5, padx=5)
        self.s4 = tk.Frame(self.main, width=750, height=50, bg="palegreen3", pady=5, padx=5)
        self.s5 = tk.Frame(self.main, width=750, height=50, bg="palegreen3", pady=5, padx=5)
        
        self.alturep = tk.Frame(self.main, width=250, height=250,  bg="palegreen3", pady=5, padx=5)


        self.s1.grid(row=0)
        self.s2.grid(row=1, column=0)
        self.alturep.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.s3.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.s4.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.s5.grid(row=5, column=0, columnspan=2, sticky="nsew")


        self.main.grid_rowconfigure(8, weight=4)
        self.main.grid_columnconfigure(2, weight=1)
        self.s2.grid_propagate(0)
        
        
#        self.s10 = tk.Frame(self.main, width=750, height=50, pady=5, padx=5, bg="palegreen1")
#        self.s10.grid(row=10, column=2, columnspan=2, sticky="nsew")   
        #self.s1.grid_propagate(0)
    
# create container frame to hold log
        self.log = tk.Frame(self.tab2, bg="palegreen3")
        self.log.pack()
        
        # Adding a Textbox Entry widget
#        scrolW  = 65; scrolH  =  25
        self.scr = scrolledtext.ScrolledText(self.log, wrap=tk.WORD, width=1000, height=1000, font=LOG_FONT)
        self.scr.pack()
       
#%% Set Back, Run, and User Guide buttons        
      
        self.back =  tk.Button(self.main, text="BACK", font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                              command=self.backtomenu)
        self.back.grid(row=10, column=0, sticky="W", padx=5, pady=5)
        
        
        #run only appears once the required files have been set
        self.run_button = tk.Button(self.main, text='RUN', fg="green", bg='lightgrey', relief='solid', borderwidth=2,
                                    command=self.run, font=TEXT_FONT)
        self.run_button.grid(row=10, column=0, sticky="E", padx=5, pady=5)
        
        self.guide = tk.Button(self.main, font=TEXT_FONT, text="User Guide", bg='lightgrey', relief='solid', borderwidth=2,
                               command=self.user_guide)
        self.guide.grid(row=1, column=0, pady=20)
#%% Setting up  directions text space
        
        self.add_instructions(self.s2, self.s1)

# %% Setting up each file upload space (includes browse button, and manual text entry for file path)
        group_label = tk.Label(self.s3, font=TEXT_FONT, bg="palegreen3", 
                             text="Name Run Group (optional):")
        group_label.grid(row=0, sticky="W")
        #group text entry
        self.group_list = tk.StringVar(self.s3)
        self.group_list_man = ttk.Entry(self.s3)
        self.group_list_man["width"] = 25
        self.group_list_man["textvariable"]= self.group_list
        self.group_list_man.grid(row=1, column=0, sticky='W', pady=20)
        
        
        self.check_altrec = tk.BooleanVar()
        self.altrec_sel = tk.Checkbutton(self.alturep, text="Use alternate receptors",
                                           variable = self.check_altrec, bg='palegreen3',
                                           command = self.set_altrec, font=TEXT_FONT)
        self.altrec_sel.grid(row=0, column=0, sticky='W')

        #facilities label
        fac_label = tk.Label(self.s3, font=TEXT_FONT, bg="palegreen3", 
                             text="1. Please select a Facilities List Options file:")
        fac_label.grid(row=3, sticky="W")
        
        #facilities upload button
        self.fac_up = tk.Button(self.s3, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                 command = lambda: self.uploadFacilitiesList())
        self.fac_up["text"] = "Browse"
        self.fac_up.grid(row=4, column=0, sticky="W")
        self.fac_up.bind('<Enter>', 
                         lambda e:self.browse("instructions/fac_browse.txt"))
       
        #facilities text entry
        self.fac_list = tk.StringVar(self.s3)
        self.fac_list_man = ttk.Entry(self.s3)
        self.fac_list_man["width"] = 100
        self.fac_list_man["textvariable"]= self.fac_list
        self.fac_list_man.grid(row=4, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.fac_list_man.bind('<Button-1>', 
                               lambda e:self.manual("instructions/fac_man.txt"))
        
                
        #Hap emissions label
        hap_label = tk.Label(self.s4, font=TEXT_FONT, bg="palegreen3",  
                             text="2. Please select the associated HAP Emissions file:")
        hap_label.grid(row=1, sticky="W")
        
        #hap emissions upload button
        self.hap_up = tk.Button(self.s4, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                 command = lambda: self.uploadHAPEmissions())
        self.hap_up["text"] = "Browse"
        self.hap_up.grid(row=2, column=0, sticky='W')
        #event handler for instructions (Button 1 is the left mouse click)
        self.hap_up.bind('<Enter>', 
                         lambda e:self.browse("instructions/hap_browse.txt"))
                
        #hap emission text entry
        self.hap_list = tk.StringVar(self.s4)
        self.hap_list_man = ttk.Entry(self.s4)
        self.hap_list_man["width"] = 100
        self.hap_list_man["textvariable"]= self.hap_list
        self.hap_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.hap_list_man.bind('<Button-1>', 
                               lambda e:self.manual("instructions/hap_man.txt"))
        
        
        #Emissions location label
        emisloc_label = tk.Label(self.s5, font=TEXT_FONT, bg="palegreen3",  
                                 text="3. Please select the associated Emissions" +
                                 " Locations file:")
        emisloc_label.grid(row=1, sticky="W")
        
        #emissions location upload button
        self.emisloc_up = tk.Button(self.s5, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                     command= lambda: self.uploadEmissionLocations())
        self.emisloc_up["text"] = "Browse"
        self.emisloc_up.grid(row=2, column=0, sticky='W')
        #event handler for instructions (Button 1 is the left mouse click)
        self.emisloc_up.bind('<Enter>', 
                             lambda e:self.browse("instructions/emis_browse.txt"))
      
        #emission loccation file text entry
        self.emisloc_list = tk.StringVar(self.s5)
        self.emisloc_list_man = ttk.Entry(self.s5)
        self.emisloc_list_man["width"] = 100
        self.emisloc_list_man["textvariable"]= self.emisloc_list
        self.emisloc_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.emisloc_list_man.bind('<Button-1>', 
                                   lambda e:self.manual("instructions/emis_man.txt"))
         
        
        #add temporal output variations
        self.check_tempvar = tk.IntVar()
        self.tempvar_sel = tk.Checkbutton(self.s5, text="Show temporal variations in the outputs", 
                                          variable = self.check_tempvar, font=TEXT_FONT,
                                          bg='palegreen3', command = self.add_temporal)
        self.tempvar_sel.grid(row=3, column=0, sticky='W', padx = 85)
        

        
    def is_valid_extension(self, filepath):
        """
        Function checks to make sure excel/csv files are selected for inputs
          
        """
        extensions = [".xls", ".xlsx", ".XLS", ".csv", ".CSV"]
        return any(ext in filepath for ext in extensions)

    def openFile(self, filename):
        """
        This function opens file dialogs for uploading inputs
        
        """

        if filename is None:
            # upload was canceled
            print("Canceled!")
            return None
        elif not self.is_valid_extension(filename):
            messagebox.showinfo("Invalid file format", 
                                "Not a valid file format, please upload an excel/csv file as per the instructions.")
            return None
        else:
            return os.path.abspath(filename)


#%% functions for uploading inputs
    
    def uploadFacilitiesList(self):
        """
        Function for uploading Facilities List option file. Also creates
        user receptor input space if indicated
        """
        
        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.uploader.upload("faclist", fullpath)

            self.model.facids = self.model.faclist.dataframe['fac_id']

            # Update the UI
            self.fac_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.faclist.log]
            
            #trigger additional inputs fo user recptors, assuming we are not in "user receptors only" mode
            if 'Y' in self.model.faclist.dataframe['user_rcpt'].tolist():
                #create user receptors
                self.add_ur()
                
            else:
                if hasattr(self, 's6'):
                    self.urep.destroy()
                    self.urep_list_man.destroy()
                    self.ur_label.destroy()
                    self.s6.destroy()
                    
            #trigger additional inputs for emisvar
            if 'Y' in self.model.faclist.dataframe['emis_var'].tolist():
                #create user receptors
                self.add_variation()
                
            else:
                if hasattr(self, ''):
                    self.emisvar_label.destroy()
                    self.emisvar_list_man.destroy()
                    self.emisvar_list.destroy()
                    self.emisvar_on.destroy()
                
            
                    
            #trigger additional inputs for building downwash
            if 'Y' in self.model.faclist.dataframe['bldg_dw'].tolist():
                
                #enable optional input tab
                self.optionaltab = True
                
                #create building downwash input
                self.add_bldgdw()
            
            else:
                if hasattr(self, 's9'):
                    self.bldgdw_up.destroy()
                    self.bldgdw_list_man.destroy()
                    self.bldgdw_label.destroy()
                    self.s9.destroy()

    def uploadHAPEmissions(self):
        """
        Function for uploading Hap Emissions file
        """
        
        try:
            
            self.model.faclist.dataframe
            
        except:
        
            messagebox.showinfo('Error', "Please upload a Facilities List Options file " +
                             "before uploading the Hap Emissions file.")
            
        else:
            
            fullpath = self.openFile(askopenfilename())
            if fullpath is not None:
                self.uploader.upload("hapemis", fullpath)
    
                # Update the UI
                self.hap_list.set(fullpath)
                [self.scr.insert(tk.INSERT, msg) for msg in self.model.hapemis.log]
            
                
            
    
    def uploadEmissionLocations(self):
        """
        Function for uploading Emissions Locations file. Also creates optional 
        input spaces if indicated in file or removes optional spaces if upload
        is triggered again and there are no optional inputs indicated
        """
        
        try: 
            
            self.model.faclist.dataframe
            
        except:
            
            messagebox.showinfo('Error', "Please upload a Facilities List Options file first")
            
            
        else:
            
            try:
            
                self.model.hapemis.dataframe
                    
            except:
            
                messagebox.showinfo('Error', "Please upload Hap Emissions file before " +
                                  "uploading the Emissions Location file")
                
            else:
  
                fullpath = self.openFile(askopenfilename())
                if fullpath is not None:
                    self.uploader.upload("emisloc", fullpath)
        
                    # Update the UI
                    self.emisloc_list.set(fullpath)
                    [self.scr.insert(tk.INSERT, msg) for msg in self.model.emisloc.log]
                    
                    #trigger additional inputs for buoyant line and polyvertex
                    if 'I' in self.model.emisloc.dataframe['source_type'].tolist():
                        
                        #enable optional input tab
                        self.optionaltab = False
                        
                        #create polyvertex upload 
                        self.add_poly()
                        
                    else:
                        #reset gui if reuploading
                        
                        if hasattr(self, 's8'):
                            self.poly_list_man.destroy()
                            self.poly_up.destroy()
                            self.poly_label.destroy()
                            self.s8.destroy()
                            
                            
                    if 'B' in self.model.emisloc.dataframe['source_type'].tolist():
                        
                        #enable optional input tab
                        self.optionaltab = False
                        
                        #create buoyant line upload
                        self.add_buoyant()
                        
                    else:
                        #reset gui if reuploading    
                         if hasattr(self, 's7'):
                            self.buoyant_list_man.destroy()
                            self.buoyant_up.destroy()
                            self.b_label.destroy()
                            self.s7.destroy()
        
                    # Deposition and depletion check
        
                    # set phase column in faclist dataframe to None
                    self.model.faclist.dataframe['phase'] = None
        
                    for i, r in self.model.faclist.dataframe.iterrows():
        
                        phase = check_phase(r)
                        #                phaseList.append([r['fac_id'], phase])
                        self.model.faclist.dataframe.at[i, 'phase'] = phase
        
                    deposition_depletion = check_dep(self.model.faclist.dataframe, self.model.emisloc.dataframe)
        
                    #pull out facilities using depdeplt
                    self.model.depdeplt = [x[0] for x in deposition_depletion]
                    print('DEPDEP:', self.model.depdeplt)
        
                    #pull out conditional inputs
                    conditional = set([y for x in deposition_depletion for y in x[1:]])
                    #print('conditional', conditional)
        
                    if conditional is not None:
                        #enable deposition and depletion input tab
                        self.deptab = True
        
        
                        #if deposition or depletion present load gas params library
                        self.uploader.uploadLibrary("gas params")
                        for required in conditional:
                            print("required", required)
                            if required == 'particle size':
                                self.add_particle()
        
                            elif required == 'land use':
                                self.add_land()
        
                            elif required == 'seasons':
                                self.add_seasons()
        
                    else:
                        # clear on new input without dep/deplt
                        if hasattr(self, 's12'):
                            # clear particle
                            if hasattr(self, 'dep_part'):
                                self.dep_part_up.destroy()
                                self.dep_part_man.destroy()
                                self.dep_part.set('')
                            #                        self.dep_part.destroy()
                            # clear land
                            if hasattr(self, 'dep_land'):
                                self.dep_land_up.destroy()
                                self.dep_land_man.destroy()
                                self.dep_land.set('')
                            #                        self.dep_land.destroy()
        
                            # clear vegetation
                            if hasattr(self, 'dep_seasons'):
                                self.dep_seasons_up.destroy()
                                self.dep_seasons_man.destroy()
                                self.dep_seasons.set('')
                            #                        self.dep_seasons.destroy()
    
                        self.s12.destroy()

    def uploadPolyvertex(self):
        """
        Function for uploading polyvertex source file
        """
        
        if self.model.emisloc.dataframe is None:
            messagebox.showinfo("Emissions Locations File Missing",
                "Please upload an Emissions Locations file before adding" +
                " a Polyvertex file.")
        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.uploader.uploadDependent("polyvertex", fullpath, 
                                                   self.model.emisloc.dataframe)


            # Update the UI
            self.poly_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.multipoly.log]

    def uploadbuoyant(self):
        """
        Function for uploading buoyant line parameter file
        """

        if self.model.emisloc.dataframe is None:
            messagebox.showinfo("Emissions Locations File Missing",
                "Please upload an Emissions Locations file before adding"+ 
                " a buoyant line file.")
        
        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.uploader.uploadDependent("buoyant line", fullpath, 
                                                   self.model.emisloc.dataframe)

            # Update the UI
            self.buoyant_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.multibuoy.log]

    def uploadUserReceptors(self):
        """
        Function for uploading user receptors
        """

        if self.model.faclist is None:
            messagebox.showinfo("Facilities List Option File Missing",
                "Please upload a Facilities List Options file before selecting"+
                " a User Receptors file.")
            return

        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:

            self.uploader.uploadDependent("user receptors", fullpath, 
                                          self.model.faclist.dataframe)
            
            self.model.model_optns['ureceptr'] = True
            # Update the UI
            self.urep_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.ureceptr.log]

    def uploadAltReceptors(self):
        """
        Function for uploading Alternate Receptors
        """

        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
                        
            self.uploader.upload("alt receptors", fullpath)
            self.model.altRec_optns["path"] = fullpath

            # Update the UI
            self.urepalt_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.altreceptr.log]

    def uploadBuildingDownwash(self):
        """ 
        Function for uploading building downwash
        """
        if self.model.faclist.dataframe is None:
            messagebox.showinfo("Facilities List Option File Missing",
                "Please upload a Facilities List Options file before selecting"+
                " a building downwash file.")

        fullpath = self.openFile(askopenfilename())
        if fullpath is not None: 
            self.uploader.uploadDependent("building downwash", fullpath, 
                                          self.model.faclist.dataframe)

            # Update the UI
            self.bldgdw_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.bldgdw.log]
    



    def uploadParticle(self, facilities):
        """ 
        Function for uploading particle size
        """
        if self.model.faclist.dataframe is None:
            messagebox.showinfo("Facilities List Option File Missing",
                "Please upload a Facilities List Options file before selecting"+
                " a particle file.")

        fullpath = self.openFile(askopenfilename())
        if fullpath is not None: 
            self.uploader.uploadDependent("particle depletion", fullpath, 
                                           self.model.faclist.dataframe, facilities)

            # Update the UI
            self.dep_part.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.partdep.log]
            
    
    
    def uploadLandUse(self):
        """ 
        Function for uploading land use information
        """
        if self.model.faclist.dataframe is None:
            messagebox.showinfo("Facilities List Option File Missing",
                "Please upload a Facilities List Options file before selecting"+
                " a particle file.")

        fullpath = self.openFile(askopenfilename())
        if fullpath is not None: 
            self.uploader.uploadDependent("land use", fullpath, 
                                          self.model.faclist.dataframe)

            # Update the UI
            self.dep_land.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.landuse.log]
            
    
    def uploadSeasons(self):
        """ 
        Function for uploading seasonal vegetation information
        """
        if self.model.faclist.dataframe is None:
            messagebox.showinfo("Facilities List Option File Missing",
                "Please upload a Facilities List Options file before selecting"+
                " a particle file.")

        fullpath = self.openFile(askopenfilename())
        if fullpath is not None: 
            self.uploader.uploadDependent("seasons", fullpath, 
                                          self.model.faclist.dataframe)

            # Update the UI
            self.dep_seasons.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.seasons.log]
    
    
    
    def uploadVariation(self):
        """
        Function for uploading emissions variation inputs
        """
        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.uploader.uploadDependent("emissions variation", fullpath, 
                                          self.model.emisloc.dataframe)
            
             # Update the UI
            self.emisvar_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.emisvar.log]
    
    
    
#%% PLace for Creating Optional Inputs    
    
        
    def create_optional(self, inputtype):
        """ function for creating optional tab"""
        
        additional = False
        dep = False
        tempvar = False
        
        #check to see what the input is
        
        if inputtype == 'buoyant':
            additional = True            
        elif inputtype == 'poly':
            additional = True   
        elif inputtype == 'bldgdw':   
            additional = True            
        elif inputtype == 'part':            
            dep =True            
        elif inputtype == 'land':
            dep =True
        elif inputtype == 'season':
            dep =True

        # determine logic for creation
        if hasattr(self, 'optionalinputtab'):
            pass
#            
        else: 
            
            if additional == True:
                
                
                #create optional input tab
                self.optionalinputtab = tk.Frame(self.tabControl, bg='palegreen3')
                self.optionalinputtab.grid_rowconfigure(10, weight=4)
                self.tabControl.insert(1, self.optionalinputtab, text='Additional Inputs')
                
                #get tab info
#                print('tabs:', self.tabControl.tabs())
#                print('number of tabs:', self.tabControl.index('end'))
#                
#                print('position', self.tabControl.index(self.tabControl.select()))
#                
                
                #destroy run button if it hasn't been but do not put it anywhere just yet
                if hasattr(self, 'run_button'):
                    self.run_button.destroy()
                
                
                #add next button to main if doesn't exist
                if hasattr(self, 'nextmain'):
                    pass
                
                else:
                
                    self.nextmain = tk.Button(self.main, font=TEXT_FONT, text='NEXT',  bg='lightgrey', relief='solid', borderwidth=2,
                                                 command = self.nexttab)
                    self.nextmain.grid(row=10, column=0, sticky='E ')
                
               
                #add next button to optional input tab
                self.nextopt = tk.Button(self.optionalinputtab, font=TEXT_FONT, text='NEXT',  bg='lightgrey', relief='solid', borderwidth=2,
                                         command = self.nexttab)
                self.nextopt.grid(row=10, column=0, sticky='E', padx=5, pady=5)
                
                
                #add back button to optional input tab
                self.optback = tk.Button(self.optionalinputtab, text="BACK", font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                      command=self.backtab)
                self.optback.grid(row=10, column=0, sticky="W", padx=5, pady=5)
                
                
                self.inst_space = tk.Frame(self.optionalinputtab, width=750, height=50, bg="palegreen3", pady=5, padx=5)
                self.inst_space.grid(row=2, column=0, sticky="nsew")
                
                self.add_optional_instructions(self.inst_space) 
                
                
            
        if hasattr(self, 'depinputtab'):
             
            pass
        
        else:
            
            if dep == True:
                
                #crete deposition inputs
                self.depinputtab = tk.Frame(self.tabControl, bg='palegreen3') 
                self.depinputtab.grid_rowconfigure(8, weight=4)
                self.tabControl.insert(1, self.depinputtab, text='Dep/Depl Inputs')
                
                          
                #destroy run button if it hasn't been but do not put it anywhere just yet
                if hasattr(self, 'run_button'):
                    self.run_button.destroy()
                    
                    
                #add next button to main if doesn't exist
                if hasattr(self, 'nextmain'):
                    pass
                
                else:
                
                    self.nextmain = tk.Button(self.main, font=TEXT_FONT, text='NEXT',  bg='lightgrey', relief='solid', borderwidth=2,
                                                 command = self.nexttab)
                    self.nextmain.grid(row=10, column=0, sticky='E ')
                
                
                #add next button
                self.nextdep = tk.Button(self.depinputtab, font=TEXT_FONT, text='NEXT',  bg='lightgrey', relief='solid', borderwidth=2,
                                         command = self.nexttab)
                self.nextdep.grid(row=10, column=0, sticky='E', padx=5, pady=5)
                
                
                #add back button
                self.depback = tk.Button(self.depinputtab, text="BACK", font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                  command=self.backtab)
                self.depback.grid(row=10, column=0, sticky="W", padx=5, pady=5)
    
                
                self.inst_space = tk.Frame(self.depinputtab, width=750, height=50, bg="palegreen3", pady=5, padx=5)
                self.inst_space.grid(row=2, column=0, sticky="nsew")
                
                self.add_optional_instructions(self.inst_space)
      
    
    def add_ur(self):
        """
        Function for creating row and upload widgets for user receptors
        """

        # set the appropriate instructions text
        browse = "instructions/urep_browse.txt"
        man = "instructions/urep_man.txt"

        #create row for user receptors
        self.s6 = tk.Frame(self.main, width=250, height=50, pady=5, padx=5, bg="palegreen3")
        self.s6.grid(row=6, column=0, columnspan=2, sticky="nsew")
        
        #user recptors label
        self.ur_label = tk.Label(self.s6, font=TEXT_FONT, bg="palegreen3", 
                             text="Please select an associated User Receptor"+
                             " file:")
        self.ur_label.grid(row=0, sticky="W")
    
        #user recptors upload button
        self.urep = tk.Button(self.s6, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                               command = lambda: self.uploadUserReceptors())
        self.urep["text"] = "Browse"
        self.urep.grid(row=1, column=0, sticky="W")
        self.urep.bind('<Enter>', 
                       lambda e:self.browse(browse))
        
        #user receptor text entry
        self.urep_list = tk.StringVar(self.s6)
        self.urep_list_man = ttk.Entry(self.s6)
        self.urep_list_man["width"] = 100
        self.urep_list_man["textvariable"]= self.urep_list
        self.urep_list_man.grid(row=1, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.urep_list_man.bind('<Button-1>', 
                                lambda e:self.manual(man))

    def add_urepalt(self):
        """
        Function for creating row and upload widgets for alternate user receptors
        """

        # set the appropriate instructions text
        browse = "instructions/urepalt_browse.txt"
        man = "instructions/urepalt_man.txt"

        #user recptors label
        self.urepalt_label = tk.Label(self.alturep, font=TEXT_FONT, bg="palegreen3",
                                  text="Please select an alternate User Receptor"+
                                      " CSV file:")
        self.urepalt_label.grid(row=1, sticky="W")

        #user recptors upload button
        self.urepaltButton = tk.Button(self.alturep, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                               command = lambda: self.uploadAltReceptors())
        self.urepaltButton["text"] = "Browse"
        self.urepaltButton.grid(row=2, column=0, sticky="W")
        self.urepaltButton.bind('<Enter>',
                       lambda e:self.browse(browse))

        #user receptor text entry
        self.urepalt_list = tk.StringVar(self.alturep)
        self.urepalt_list_man = ttk.Entry(self.alturep)
        self.urepalt_list_man["width"] = 100
        self.urepalt_list_man["textvariable"]= self.urepalt_list
        self.urepalt_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.urepalt_list_man.bind('<Button-1>',
                                lambda e:self.manual(man))

    def add_buoyant(self):
        """
        Function for creating row and buoyant line parameter upload widgets
        """
        
        #if optional input tab already exists
        if hasattr(self, "optionalinputtab"):
            
            if self.hiddenoptab == True:
              
              self.tabControl.add(self.optionalinputtab, text='Additional Inputs')
              
              self.hiddenoptab = False
            
        else:
            self.create_optional('buoyant')

         #create row for buoyant line input
        self.s7 = tk.Frame(self.optionalinputtab, width=250, height=50, pady=5, padx=5, bg="palegreen3")
        self.s7.grid(row=3, column=0, columnspan=2, sticky="nsew")
        
        
        #Buoyant Line  label
        self.b_label = tk.Label(self.s7, font=TEXT_FONT, bg="palegreen3",  
                                 text="Please select associated Buoyant Line"+
                                 " Source Parameter file:")
        self.b_label.grid(row=1, sticky="W")
        
        #buoyant line file upload button
        self.buoyant_up = tk.Button(self.s7, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                     command = lambda: self.uploadbuoyant())
        self.buoyant_up["text"] = "Browse"
        self.buoyant_up.grid(row=2, column=0, sticky='W')
        #event handler for instructions (Button 1 is the left mouse click)
        self.buoyant_up.bind('<Enter>', 
                             lambda e:self.browse("instructions/buoyant_browse.txt"))
        
        
        #buoyant line file text entry
        self.buoyant_list = tk.StringVar(self.s7)
        self.buoyant_list_man = ttk.Entry(self.s7)
        self.buoyant_list_man["width"] = 100
        self.buoyant_list_man["textvariable"]= self.buoyant_list
        self.buoyant_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.buoyant_list_man.bind('<Button-1>', 
                                   lambda e:self.manual("instructions/buoyant_browse.txt"))
    
    
    
    def add_poly(self):
        """
        Function for creating row and polyvertex file upload widgets
        """
        #if optional input tab already exists
        if hasattr(self, "optionalinputtab"):
            
            if self.hiddenoptab == True:
              
              self.tabControl.add(self.optionalinputtab, text='Additional Inputs')
              
              self.hiddenoptab = False
            
        
        else:
            self.create_optional('poly')
            print('in this run it doesnt exists!!!')

                            
        #create row for poly
        self.s8 = tk.Frame(self.optionalinputtab, width=250, height=50, pady=5, padx=5, bg="palegreen3")
        self.s8.grid(row=4, column=0, columnspan=2, sticky="nsew")
        
        #Polygon sources label
        self.poly_label = tk.Label(self.s8, font=TEXT_FONT, bg="palegreen3",  
                              text="Please select associated Polyvertex file.")
        self.poly_label.grid(row=1, sticky="W")
        
        #polygon sources upload button
        self.poly_up = tk.Button(self.s8, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                  command = lambda: self.uploadPolyvertex())
        self.poly_up["text"] = "Browse"
        self.poly_up.grid(row=2, column=0, sticky="W")
        #event handler for instructions (Button 1 is the left mouse click)
        self.poly_up.bind('<Enter>', 
                          lambda e:self.browse("instructions/poly_browse.txt"))
       
        #polygon sources loccation file text entry
        self.poly_list = tk.StringVar(self.s8)
        self.poly_list_man = ttk.Entry(self.s8)
        self.poly_list_man["width"] = 100
        self.poly_list_man["textvariable"]= self.poly_list
        self.poly_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.poly_list_man.bind('<Button-1>', 
                                lambda e:self.manual("instructions/poly_browse.txt"))
    
    
    def add_bldgdw(self):
        """ 
        Function for creating row and building downwash file upload widgets
        """

        #if optional input tab already exists
        if hasattr(self, "optionalinputtab"):
            
            if self.hiddenoptab == True:
              
              self.tabControl.add(self.optionalinputtab, text='Additional Inputs')
              
              self.hiddenoptab = False
            
        
        else:
            #create optional input tab
            print('In this run it doesnt exist')
            self.create_optional('bldgdw')
        
        #create row for building downwash
        self.s9 = tk.Frame(self.optionalinputtab, width=250, height=50, padx=5, bg="palegreen3")
        self.s9.grid(row=5, column=0, columnspan=2, sticky="nsew")
        
        # building dw labels
        self.bldgdw_label = tk.Label(self.s9,
                                     text="Please select associated Building" + 
                                     " Dimensions file", font=TEXT_FONT, bg="palegreen3")
        self.bldgdw_label.grid(row=1, sticky="W")
        
        #building dw upload button
        self.bldgdw_up = tk.Button(self.s9, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                    command = lambda: self.uploadBuildingDownwash())
        self.bldgdw_up["text"] = "Browse"
        self.bldgdw_up.grid(row=2, column=0, sticky="W")
        #event handler for instructions (Button 1 is the left mouse click)
        self.bldgdw_up.bind('<Enter>', 
                          lambda e:self.browse("instructions/bd_browse.txt"))
        
        #polygon sources loccation file text entry
        self.bldgdw_list = tk.StringVar(self.s9)
        self.bldgdw_list_man = ttk.Entry(self.s9)
        self.bldgdw_list_man["width"] = 100
        self.bldgdw_list_man["textvariable"]= self.bldgdw_list
        self.bldgdw_list_man.grid(row=2, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.bldgdw_list_man.bind('<Button-1>', 
                                lambda e:self.manual("instructions/bd_man.txt"))
        
        
        
    def add_particle(self):
        """
        Function for creating column for particle size file upload widgets
        """
        
        #if deposition/depletion input tab already exists
        if hasattr(self, "depinputtab"):
           
            if self.hiddendeptab == True:
              
              self.tabControl.add(self.depinputtab, text='Additional Inputs')
            
              self.hiddendeptab = False
        
        else:
            #create optional input tab
            self.create_optional('part')
        
        #create column for particle size file
        self.s10 = tk.Frame(self.depinputtab, width=250, height=50, pady=5, padx=5, bg="palegreen3")
        self.s10.grid(row=3, column=0, columnspan=2, sticky="nsew")
        
        #particle size label
        part_label = tk.Label(self.s10, font=TEXT_FONT, bg="palegreen3", 
                              text="Upload the file containing size information for particle matter emissions:")
        part_label.grid(row=0, sticky="W")
    
        #particle depositionsize file upload button
        self.dep_part_up = tk.Button(self.s10, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                      command = lambda: self.uploadParticle(self.model.depdeplt))
        self.dep_part_up["text"] = "Browse"
        self.dep_part_up.grid(row=1, column=0, sticky="W")
        self.dep_part_up.bind('<Enter>', 
                              lambda e:self.browse("instructions/dep_part_browse.txt"))
         
        #particle size file text entry
        self.dep_part = tk.StringVar(self.s10)
        self.dep_part_man = ttk.Entry(self.s10)
        self.dep_part_man["width"] = 100
        self.dep_part_man["textvariable"]= self.dep_part
        self.dep_part_man.grid(row=1, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.dep_part_man.bind('<Button-1>', 
                               lambda e:self.manual("instructions/dep_part_man.txt"))
              
        
    def add_land(self):
        
        """
        Function for creating column for land use upload widgets
        """
         #if deposition/depletion input tab already exists
        if hasattr(self, "depinputtab"):
            
            if self.hiddendeptab == True:
              
              self.tabControl.add(self.depinputtab, text='Additional Inputs')
            
              self.hiddendeptab = False
        
        else:
            
            self.create_optional('land')
        
        #create column for land use file
        self.s11 = tk.Frame(self.depinputtab, width=250, height=50, pady=5, padx=5, bg="palegreen3")
        self.s11.grid(row=4, column=0, columnspan=2, sticky="nsew")
        
        #land use size label
        land_label = tk.Label(self.s11, font=TEXT_FONT, bg="palegreen3", 
                              text="Upload the file containing land use information:")
        land_label.grid(row=0, sticky="W")
    
        #laand use file upload button
        self.dep_land_up = tk.Button(self.s11, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                      command = lambda: self.uploadLandUse())
        self.dep_land_up["text"] = "Browse"
        self.dep_land_up.grid(row=1, column=0, sticky="W")
        self.dep_land_up.bind('<Enter>', 
                              lambda e:self.browse("instructions/dep_land_browse.txt"))
         
        #land use file text entry
        self.dep_land = tk.StringVar(self.s11)
        self.dep_land_man = ttk.Entry(self.s11)
        self.dep_land_man["width"] = 100
        self.dep_land_man["textvariable"]= self.dep_land
        self.dep_land_man.grid(row=1, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.dep_land_man.bind('<Button-1>', 
                               lambda e:self.manual("instructions/dep_land_man.txt"))
        
        
    def add_seasons(self):
        """
        Function for creating column for seasonal vegetation upload widgets
        """
         #if deposition/depletion input tab already exists
        if hasattr(self, "depinputtab"):
           
            if self.hiddendeptab == True:
              
              self.tabControl.add(self.depinputtab, text='Additional Inputs')
              
              self.hiddendeptab = False
            
        else:
            #create optional input tab
            self.create_optional('season')
        

        #create column for land use file
        self.s12 = tk.Frame(self.depinputtab, width=250, height=50, pady=5, padx=5, bg="palegreen3")
        self.s12.grid(row=5, column=0, columnspan=2, sticky="nsew")
        
        #land use size label
        seasons_label = tk.Label(self.s12, font=TEXT_FONT, bg="palegreen3", 
                             text="Upload the file containing seasonal vegetation information:")
        seasons_label.grid(row=0, sticky="W")
    
        #laand use file upload button
        self.dep_seasons_up = tk.Button(self.s12, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                                     command = lambda: self.uploadSeasons())
        self.dep_seasons_up["text"] = "Browse"
        self.dep_seasons_up.grid(row=1, column=0, sticky="W")
        self.dep_seasons_up.bind('<Enter>', 
                             lambda e:self.browse("instructions/dep_veg_browse.txt"))
         
        #land use file text entry
        self.dep_seasons = tk.StringVar(self.s12)
        self.dep_seasons_man = ttk.Entry(self.s12)
        self.dep_seasons_man["width"] = 100
        self.dep_seasons_man["textvariable"]= self.dep_seasons
        self.dep_seasons_man.grid(row=1, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        self.dep_seasons_man.bind('<Button-1>', 
                              lambda e:self.manual("instructions/dep_veg_man.txt"))
        
    def add_variation(self):
        """
        Function for creating emission variation input space
        """
            
        #create row for emissions variation
#                self.s5 = tk.Frame(self.main, width=250, height=100, bg="palegreen3", pady=5, 
#                                    padx=5)
#                self.s5.grid(row=4, column=0, columnspan=2, sticky="nsew")
        
        #emissions variation label
        self.emisvar_label = tk.Label(self.s5, font=TEXT_FONT, bg="palegreen3", 
                             text="Please select an Emissions Variation"+
                             " file:")
        self.emisvar_label.grid(row=6, sticky="W")
    
        #emissions variation upload button
        self.emisvar_on = tk.Button(self.s5, font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                               command = lambda: self.uploadVariation())
        self.emisvar_on["text"] = "Browse"
        self.emisvar_on.grid(row=7, column=0, sticky="W")
        #self.emisvar_on.bind('<Enter>', 
                       #lambda e:self.browse("instructions/urep_browse.txt"))
        
        #emissions variation text entry
        self.emisvar_list = tk.StringVar(self.s5)
        self.emisvar_list_man = ttk.Entry(self.s5)
        self.emisvar_list_man["width"] = 100
        self.emisvar_list_man["textvariable"]= self.emisvar_list
        self.emisvar_list_man.grid(row=7, column=0, sticky='E', padx=85)
        #event handler for instructions (Button 1 is the left mouse click)
        #self.emisvar_list_man.bind('<Button-1>', 
        #lambda e:self.manual("instructions/urep_man.txt"))
                    


    def add_temporal(self):
        
        
        if self.check_tempvar.get() == 1:
            #emissions variation label
                self.tempvar_label = tk.Label(self.s5, font=TEXT_FONT, bg="palegreen3", 
                                     text="What diurnal (hourly) resolution would you like?")
                self.tempvar_label.grid(row=5, column=0, sticky="W", padx=85, pady=20)
             
                self.tkvar = tk.StringVar(self.s5)
                choices = {1, 2, 3, 4, 6, 8, 12, 24}
                self.tkvar.set(1) # set the default option

                self.popupMenu = tk.OptionMenu(self.s5, self.tkvar, *choices)
                self.popupMenu.grid(row=5, column=0, sticky="E", padx = 300, pady=10)
                
                #add emissions variation checkbox
                self.check_dr = tk.IntVar()
                self.dr_sel = tk.Checkbutton(self.s5, text="Include seasonal variations in diurnally\n resolved concentrations output", 
                                          variable = self.check_dr, font=TEXT_FONT,
                                          bg='palegreen3')
                self.dr_sel.grid(row=5, column=0, sticky="E")
                
        
        
        
        #if checked and then unchecked
        elif self.check_tempvar.get() == 0:
            if hasattr(self, 'tempvar_label'):
                    self.popupMenu.destroy()
                    self.tempvar_label.destroy()
                    self.dr_sel.destroy()
    
    def set_altrec(self):
        self.model.altRec_optns['altrec'] = self.check_altrec.get()

        if self.model.altRec_optns['altrec']:
            self.add_urepalt()
        else:
            if self.urepaltButton is not None:
                self.urepaltButton.destroy()
                self.urepalt_list_man.destroy()
                self.urepalt_label.destroy()
            
 #%% Event handlers for porting instructions

    #reset instructions space
    def reset_instructions(self):
        """
        Function clears instructions from display box 
        """
        global instruction_instance
        self.instruction_instance.set(" ")    
        
    #general function for browsing instructions
    def browse(self, location):
        """
        Function looks up text file with instructions for specified input
        browse buttons
        """
        global instruction_instance
        self.read_inst = open(location, 'r')
        self.instruction_instance.set(self.read_inst.read())
        
    #general function for manual uploads    
    def manual(self, location):
        """
        Function looks up text file with instructions for specified input 
        text fields
        """
        global instruction_instance
        self.read_inst = open(location, 'r')
        self.instruction_instance.set(self.read_inst.read())
        
    def nexttab(self):
        
        total = self.tabControl.index('end')
                
        pos = self.tabControl.index(self.tabControl.select())
        
        if pos == 0:
            
            self.tabControl.select(1)
            
        elif pos == 1:
            
            if total == 4:
               
                self.run()
            
            else:
                
                self.tabControl.select(2)
            
        elif pos == 2:
            
            self.run()
            
            
    
    def backtab(self):
        total = self.tabControl.index('end')
                
        pos = self.tabControl.index(self.tabControl.select())
        
        if pos == 1:
            
            self.tabControl.select(0)
            
        elif pos == 2:
            
            self.tabControl.select(1)
            


        
             
#%% Run function with checks if somethign is missing raise the error here and 
#   create an additional dialogue before trying to run the file

    def run(self):
        """ 
        Function passes model class to InputChecker class, then uses returned 
        dictionary to either run HEM4 or display user input error.
        
        To run each facility, function loops through facility ids and logs 
        returned errors and messages to the log tab via the queue method
        
        When all facilites are done the GUI is reset and all optional inputs
        are destroyed
        """

        self.ready = False
        
        #add temp_var to model ## add to checks 
        if self.check_tempvar.get() == 1:
            self.model.temporal = True
            self.model.tempvar = int(self.tkvar.get())
            self.model.seasonvar = True if self.check_dr.get() == 1 else False
        else:
            self.model.temporal = False

        #Check inputs
        check_inputs = InputChecker(self.model)
        
        try:
            required = check_inputs.check_required()
            
        except Exception as e:
                
                Logger.logMessage(str(e))
                
        else:
            if 'ready' not in required['result']:
                messagebox.showinfo('Error', required['result'])
                self.ready = False
                
            elif required['dependencies'] is not []:
                try:
                    
                    optional = check_inputs.check_dependent(required['dependencies'])
                    
                except Exception as e:
                    
                    Logger.logMessage(str(e))
                    
                else:
                    
                
                    if 'ready' not in optional['result']:
                        messagebox.showinfo('Error', optional['result'])
                        self.ready = False
                    
                    else:
                        self.ready = True
                        
                        
                        #get deposition exclusions
                        print('Checking depletion.... against', self.model.depdeplt)
                        
                        #look through hapemis for facilities that are running deposition or depletion
                        hapDep = self.model.hapemis.dataframe[self.model.hapemis.dataframe['fac_id'].isin(self.model.depdeplt)]
                        
                        #now check phase in facilities list option file
                        facDep = self.model.faclist.dataframe[self.model.faclist.dataframe['fac_id'].isin(self.model.depdeplt)]
                        
                        
                        
                        for i, r in facDep.iterrows():
                            if r['phase'] in ['P', 'V', 'B']:
                                
                                #look at pollutants
                                pols = hapDep[hapDep['fac_id'] == r['fac_id']]
                                
                                #get sourcelist
                                sourcesList = set(pols['source_id'].tolist())
                                #print(r['fac_id'], r['phase'], 'Sources:', sourcesList)
                                
                                for source in sourcesList:
                                    print('Source', source)
                                    
                                    if r['phase'] == 'P':
                                        #get the sum of part frac
                                        polSum = sum(pols[pols['source_id'] == source]['part_frac'].tolist())
                                        print('P PolSum:', polSum)
                                        
                                        #if they are zero then its not particulate at all 
                                        if polSum == 0:
                                            
                                            #add it to the list of source exclusions
                                            self.model.sourceExclusion.append(source)
                                        
                                    elif r['phase'] == 'V':
                                        
                                        #get
                                        so = pols[pols['source_id'] == source]['part_frac'].tolist()
                                        print('V:', so)
                                        polSum = sum(so)
                                        allPart = len(so) * 100
                                        
                                        #if they are all particle (100%)
                                        if polSum == allPart:
                                            
                                            #add it to the list of source exclusions
                                            self.model.sourceExclusion.append(source)
                            
                            else:
                                self.ready = True
        

       #%%if the object is ready
        if self.ready == True:

            #tell user to check the Progress/Log section
            override = messagebox.askokcancel("Confirm HEM4 Run", "Clicking 'OK'"+
                                   " will start HEM4. Check the log tabs for" +
                                   " updates on facility runs.")

            if override:
                global instruction_instance
                self.instruction_instance.set("HEM4 Running, check the log tab for updates")
                self.tab2.lift()
                Logger.logMessage("\nHEM4 is starting...")
                
                 #set run name
                if len(self.group_list.get()) > 0:
                    self.model.group_name = self.group_list.get()
                    
                    
                else:
                    
                    self.model.group_name = None
                    
                if hasattr(self, 'run_button'):
                    self.run_button.destroy()
                
                self.stop = tk.Button(self.main, text="STOP", fg="red", font=TEXT_FONT, bg='lightgrey', relief='solid', borderwidth=2,
                              command=self.quit_app)
                self.stop.grid(row=0, column=0, sticky="E", padx=5, pady=5)
        
                try:
                    self.process()
                    
                except Exception as e:
                
                    Logger.logMessage(str(e))
                

    def process(self):
        """
        Function creates thread for running HEM4 concurrently with tkinter GUI
        """
        executor = ThreadPoolExecutor(max_workers=1)

        self.running = True
        self.disable_buttons()
        
        self.processor = Processor(self.model, Event())
        future = executor.submit(self.processor.process)
        future.add_done_callback(self.processing_finish)

    def processing_finish(self, future):
        """
        Callback that gets run in the same thread as the processor, after the target method
        has finished. It's purpose is to update the shared callback queue so that the main
        thread can update the GUI (which cannot be done in this thread!)
        :param future:
        :return: None
        """
        self.callbackQueue.put(self.finish_run)

    def finish_run(self):
        """
        Return Hem4 running state to False, and either reset or quit the GUI, depending on
        whether or not the processing finished naturally or was aborted.
        :return: None
        """
        self.running = False

        if self.aborted:
            self.reset_gui()
        else:
            self.reset_gui()

    def check_processing(self):
        """
        Check the callback queue to see if the processing thread has indicated that
        it's finished running. If an entry is found, it's the method to run that
        instructs this class how to reset/kill the GUI. If not, schedule another
        check soon.
        :return: None
        """
        try:
            callback = self.callbackQueue.get(block=False)
        except queue.Empty: #raised when queue is empty
            self.after(500, self.check_processing)
            return

        print("About to call callback...")
        callback()

    def after_callback(self):
        """
        Function listens on thread RUnning HEM4 for error and completion messages
        logged via queue method
        """
        try:
            message = self.messageQueue.get(block=False)
        except queue.Empty:
            # let's try again later
            self.after(25, self.after_callback)
            return

        print('after_callback got', message)
        if message is not None:
            self.scr.configure(state='normal')
            self.scr.insert(tk.INSERT, message)
            self.scr.insert(tk.INSERT, "\n")
            self.scr.configure(state='disabled')
            self.after(25, self.after_callback)
