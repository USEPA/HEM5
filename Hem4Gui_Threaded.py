# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 10:26:13 2017

@author: dlindsey
"""
import os
import concurrent.futures as futures
import queue
import tkinter as tk
import traceback
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk
import Hem4_Input_Processing as prepare
from model.Model import Model
from runner.FacilityRunner import FacilityRunner
from upload.FileUploader import FileUploader
from tkinter.filedialog import askopenfilename


#%% Hem4 GUI
from writer.kml.KMLWriter import KMLWriter


class Hem4():

    def __init__ (self):
        #create window instance
        self.win = tk.Tk()
    
        #title
        self.win.title("HEM4")
        self.win.maxsize(1000, 1000)
        self.createWidgets()
        self.running = False

        # Create the model
        self.model = Model()

        # Create a file uploader
        self.uploader = FileUploader(self.model)

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
        self.fac_up = ttk.Button(self.s3, command = lambda: self.uploadFacilitiesList())
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
        self.hap_up = ttk.Button(self.s4, command = lambda: self.uploadHAPEmissions())
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
        self.emisloc_up = ttk.Button(self.s5, command= lambda: self.uploadEmissionLocations())
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
        self.ur_op = ttk.Checkbutton(self.s8, text="Include user receptors for any facilities, as indicated in the Facilities List Options file.",
             variable=self.u_receptors, command=self.add_ur).grid(row=1, column=1, sticky="w")


    def is_excel(self, filepath):
        extensions = [".xls", ".xlsx"]
        return any(ext in filepath for ext in extensions)

    def openFile(self, filename):

        if filename is None:
            # upload was canceled
            print("Canceled!")
            return None
        elif not self.is_excel(filename):
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file.")
            return None
        else:
            return os.path.abspath(filename)

    def uploadFacilitiesList(self):
        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.uploader.upload("faclist", fullpath)

            self.model.facids = self.model.faclist.dataframe['fac_id']

            # Update the UI
            self.fac_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.faclist.log]

    def uploadHAPEmissions(self):
        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.uploader.upload("hapemis", fullpath)

            # Update the UI
            self.hap_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.hapemis.log]

    def uploadEmissionLocations(self):
        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.uploader.upload("emisloc", fullpath)

            # Update the UI
            self.emisloc_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.emisloc.log]

    def uploadPolyvertex(self):

        if not hasattr(self, "emisloc_df"):
            messagebox.showinfo("Emissions Locations File Missing",
                "Please upload an Emissions Locations file before adding a Polyvertex file.")

        result = self.uploader.uploadDependent("polyvertex", self.emisloc_df)

        # Update the global model
        self.multipoly_df = result['df']

        # Update the UI
        self.poly_list.set(result['path'])
        [self.scr.insert(tk.INSERT, msg) for msg in result['messages']]

    def uploadBouyant(self):

        if not hasattr(self, "emisloc_df"):
            messagebox.showinfo("Emissions Locations File Missing",
                "Please upload an Emissions Locations file before adding a Bouyant line file.")

        result = self.uploader.uploadDependent("bouyant", self.emisloc_df)

        # Update the global model
        self.bouyant_df = result['df']

        # Update the UI
        self.poly_list.set(result['path'])
        [self.scr.insert(tk.INSERT, msg) for msg in result['messages']]

    def uploadUserReceptors(self):

        if self.model.faclist.dataframe is None:
            messagebox.showinfo("Facilities List Option File Missing",
                "Please upload a Facilities List Options file before selecting a User Receptors file.")

        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.uploader.uploadDependent("user receptors", fullpath, self.model.faclist.dataframe)

            # Update the UI
            self.urep_list.set(fullpath)
            [self.scr.insert(tk.INSERT, msg) for msg in self.model.ureceptr.log]

    def add_ur(self):
        #when box is checked add row with input
        if self.u_receptors.get() == True:
            
            #user recptors upload button
            self.urep = ttk.Button(self.s8, command = lambda: self.uploadUserReceptors())
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

        # Upload the Dose response library
        fullpath = r"resources/Dose_response_library.xlsx"
        self.uploader.upload("haplib", fullpath)

        #make sure fac_list df was created correctly
        if self.model.faclist.dataframe is not None:
            
            if self.model.faclist.dataframe.empty:
                messagebox.showinfo("Error","There was an error uploading Facilities List Option File, please try again")
                check1 = False
                
            else:
                fids = set(self.model.facids)
               # print("fac_list ready")
                check1 = True
        else:
            check1 = False
            messagebox.showinfo("Error","There was an error uploading Facilities List Option File, please try again")
       
        #make sure emis_loc df was created correctly
        if self.model.emisloc.dataframe is not None:
            
            if self.model.emisloc.dataframe.empty:
                messagebox.showinfo("Error","There was an error uploading Emissions Locations File, please try again")
                check2 = False
            else:
                #check facility id with emis loc ids
                efids = set(self.model.emisloc.dataframe['fac_id'])
                esource = set(self.model.emisloc.dataframe['source_id'])
                if efids == fids:
                    #print("emis_locs ready")
                    check2 = True
                
        else:
            check2 = False
            messagebox.showinfo("Error","There was an error uploading Emissions Locations File, please try again")

       #make sure hap_emis  df was created correctly
        if self.model.hapemis.dataframe is not None:
            
            
            if self.model.hapemis.dataframe.empty:
                messagebox.showinfo("Error","There was an error uploading HAP Emissions File, please try again")
                check3 = False
                #print("empty")
            else:
                #check emis locations and source ids
                hfids = set(self.model.hapemis.dataframe['fac_id'])
                hsource = set(self.model.hapemis.dataframe['source_id'])
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
            user_rec_check = self.model.faclist.dataframe['user_rcpt'] == 'Y'
            user_rec_checklist = []
            
                
            if True in user_rec_check.values:
                
                if self.model.ureceptr.dataframe is not None:
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
                
                   
            if hasattr(self, 'multipoly_df') and hasattr(self, 'multibuoy_df') and self.model.ureceptr.dataframe is not None:
                self.ready = True
                print("Ready to run!")
            
        
       #%%if the object is ready
                if self.ready == True:
                   
                    #tell user to check the Progress/Log section
                    messagebox.askokcancel("Confirm HEM4 Run", "Clicking 'OK' will start HEM4.")
                   
                    #create object for prepare inputs
                    self.running = True
                   
                    #create a Google Earth KML of all sources to be modeled
                    kmlWriter = KMLWriter()
                    if kmlWriter is not None:
                        kmlWriter.write_kml_emis_loc(self.model)

                    the_queue.put("\nPreparing Inputs for " + str(self.model.facids.count()) + " facilities")
                    inputPrep = prepare.Prepare_Inputs(self.model)

                    # let's tell after_callback that this completed
                    #print('thread_target puts None to the queue')
                   
                   
                    fac_list = []
                    for index, row in self.model.faclist.dataframe.iterrows():

                       facid = row[0]
                       fac_list.append(facid)
                       num = 1
        
                    for facid in fac_list:
                        
                        #save version of this gui as is? constantly overwrite it once each facility is done?
                        the_queue.put("\nRunning facility " + str(num) + " of " + str(len(fac_list)))

                        runner = FacilityRunner(facid, the_queue, inputPrep)
                        runner.run()

                        #increment facility count
                        num += 1

                the_queue.put("\nFinished running all facilities.\n")
                
                #reset all inputs if everything finished
                self.model.reset()
                self.fac_list.set('')
                self.hap_list.set('')
                self.emisloc_list.set('')
                self.urep_list.set('')

                self.running = False

    def workerComplete(self, future):
        ex = future.exception()

        if ex is not None:
            # logger = logging.getLogger('workerComplete')
            # logger.exception(ex)
            fullStackInfo = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
            the_queue.put("\nAn error ocurred while running a facility:")
            the_queue.put("\n\n" + fullStackInfo)

    #%% Create Thread for Threaded Process
    def runThread(self):
        global instruction_instance
        instruction_instance.set("Hem4 Running, check the log tab for updates")

        executor = futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.run)
        future.add_done_callback(self.workerComplete)


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
