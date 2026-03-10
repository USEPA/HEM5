# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 12:18:33 2025

merge.py - GUI for the merging of two HEM runs.
"""

from datetime import datetime

from com.sca.hem4.gui.Page import Page
import tkinter as tk
import tkinter.ttk as ttk
import PIL.Image
from PIL import ImageTk
from functools import partial
from tkinter.filedialog import askopenfilename
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox
from com.sca.hem4.gui.Styles import TEXT_FONT, SMALL_TEXT_FONT, TITLE_FONT, MAIN_COLOR, HIGHLIGHT_COLOR, SUBTITLE_FONT
from com.sca.hem4.gui.EntryWithPlaceholder import EntryWithPlaceholder
import tkinter.font as TkFont
from com.sca.hem4.tools.MergeHemRuns import MergeHemRuns
from com.sca.hem4.log.Logger import Logger


class Merge(Page):
    
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.home = nav
                
        self.container = tk.Frame(self, bg=self.tab_color, bd=2)
        self.container.pack(side="top", fill="both", expand=True)

        # Create grid
        self.title_frame = tk.Frame(self.container, height=80, bg=self.tab_color)
        self.blankrow1_frame = tk.Frame(self.container, height=20, bg=self.tab_color)
        self.folder1_title_frame = tk.Frame(self.container, height=120, pady=1, padx=5, bg=self.tab_color)
        self.folder1_frame = tk.Frame(self.container, height=120, pady=1, padx=5, bg=self.tab_color)
        self.blankrow2_frame = tk.Frame(self.container, height=20, bg=self.tab_color)
        self.folder2_title_frame = tk.Frame(self.container, height=120, pady=1, padx=5, bg=self.tab_color)
        self.folder2_frame = tk.Frame(self.container, height=120, pady=1, padx=5, bg=self.tab_color)
        self.info_frame = tk.Frame(self.container, height=120, pady=1, padx=5, bg=self.tab_color)
        self.run_frame = tk.Frame(self.container, height=100, pady=1, padx=5, bg=self.tab_color)

        self.title_frame.grid(row=1, columnspan=2, sticky="nsew")
        self.blankrow1_frame.grid(row=2, columnspan=2, sticky="ew")
        self.folder1_title_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.folder1_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.blankrow2_frame.grid(row=5, columnspan=2, sticky="ew")
        self.folder2_title_frame.grid(row=6, columnspan=2, sticky="nsew")
        self.folder2_frame.grid(row=7, columnspan=2, sticky="nsew")
        self.info_frame.grid(row=8, columnspan=2, sticky="nsew")
        self.run_frame.grid(row=9, columnspan=2, sticky="ew")

        # Create title
        self.title_image = PIL.Image.open('images\icons8-merge-documents-64-white.png').resize((36,36))
        self.tticon = self.add_margin(self.title_image, 5, 0, 5, 0)
        self.titleicon = ImageTk.PhotoImage(self.tticon)
        self.titleLabel = tk.Label(self.title_frame, image=self.titleicon, bg=self.tab_color)
        self.titleLabel.image = self.titleicon # keep a reference!
        self.titleLabel.grid(row=1, column=0, padx=10, pady=1)
        title = tk.Label(self.title_frame, text="MERGE TWO HEM RUNS", font=TITLE_FONT,
                         fg=MAIN_COLOR, bg=self.tab_color, anchor="w")
        title.grid(row=1, column=1, pady=2, padx=10, sticky="w")

        # First step - choose the original rungroup folder
        self.folder1_title = tk.Label(self.folder1_title_frame, text="Original HEM rungroup folder:", font=TEXT_FONT,
                         bg=self.tab_color, anchor="w")
        self.folder1_title.grid(row=0, column=0, pady=2, padx=10)

        self.fu = PIL.Image.open('images\icons8-folder-48.png').resize((30,30))
        self.ficon = self.add_margin(self.fu, 5, 0, 5, 0)
        self.fileicon = ImageTk.PhotoImage(self.ficon)
        self.fileLabel = tk.Label(self.folder1_frame, image=self.fileicon, bg=self.tab_color
                                  , anchor='w')
        self.fileLabel.image = self.fileicon # keep a reference!
        self.fileLabel.grid(row=0, column=0, padx=10, sticky="w")

        self.step1_instructions = tk.Label(self.folder1_frame,
                                      text="Select folder containing the original HEM run results"
                                      , font=TITLE_FONT, bg=self.tab_color)
        self.step1_instructions.grid(row=0, column=1, padx=10, sticky='w')
        # self.fileLabel.bind("<Button-1>", partial(self.origBrowse, self.step1_instructions))

        self.step1_instructions.bind("<Button-1>", partial(self.origBrowse, self.step1_instructions))

        # Secojnd step - choose the rerun rungroup folder
        self.folder2_title = tk.Label(self.folder2_title_frame, text="New/Rerun HEM rungroup folder:", font=TEXT_FONT,
                         bg=self.tab_color, anchor="w")
        self.folder2_title.grid(row=0, column=0, pady=2, padx=10)

        self.info_text = 'Note: These new results will be merged into the Original HEM rungroup folder. Any facilities with the same name in the Original folder will be replaced by facilities from the New/Rerun folder. Any additional facilities in the New/Rerun folder (not already in the Original folder) will be added to the Original folder.'
        self.info_title = tk.Message(self.info_frame, text=self.info_text, font=TEXT_FONT,
                         bg=self.tab_color, anchor="w", width=450, padx=100)
        self.info_title.grid(row=0, column=0, pady=2, padx=10)

        fu2 = PIL.Image.open('images\icons8-folder-48.png').resize((30,30))
        ficon2 = self.add_margin(fu2, 5, 0, 5, 0)
        fileicon2 = ImageTk.PhotoImage(ficon2)
        self.fileLabel2 = tk.Label(self.folder2_frame, image=fileicon2, bg=self.tab_color)
        self.fileLabel2.image = fileicon2 # keep a reference!
        self.fileLabel2.grid(row=0, column=0, padx=10)

        self.step2_instructions = tk.Label(self.folder2_frame,
                                      text="Select folder containing the new HEM run results", font=TITLE_FONT, bg=self.tab_color, anchor="w")
        self.step2_instructions.grid(row=0, column=1, pady=10, padx=10)
        self.fileLabel2.bind("<Button-1>", partial(self.newBrowse, self.step2_instructions))

        self.step2_instructions.bind("<Button-1>", partial(self.newBrowse, self.step2_instructions))


        self.run_button = tk.Label(self.run_frame, text="Run", bg='lightgrey', relief='solid',
                              font=TEXT_FONT, borderwidth=2)
        self.run_button.grid(row=0, column=0, sticky='ew', padx=20, pady=20)
        self.run_button.bind("<Button-1>", self.run)


    def origBrowse(self, icon, event):

        if 'disabled' in self.fileLabel.config('state'):
            return
        
        self.origPath = tk.filedialog.askdirectory()
        # Make sure a directory was selected
        if self.origPath:
            icon["text"] = self.origPath.split("/")[-1]

    def newBrowse(self, icon, event):

        if 'disabled' in self.fileLabel2.config('state'):
            return
        
        self.newPath = tk.filedialog.askdirectory()
        # Make sure a directory was selected
        if self.newPath:
            icon["text"] = self.newPath.split("/")[-1]


    def run(self, event):

        # Make sure two directories were selected
        try:
            self.origPath
            
            if not self.origPath:
                messagebox.showinfo("Folder not selected", "An original HEM rungroup folder was not selected. Please select one before running this tool.")
                return
                
        except AttributeError:
            messagebox.showinfo("Folder not selected", "An original HEM rungroup folder was not selected. Please select one before running this tool.")
            return
        
        try:
            self.newPath
            
            if not self.newPath:
                messagebox.showinfo("Folder not selected", "A folder of new HEM results was not selected. Please select one before running this tool.")
                return
            
        except AttributeError:
            messagebox.showinfo("Folder not selected", "A folder of new HEM results was not selected. Please select one before running this tool.")
            return
        
        # Confirm this app should be run
        result = messagebox.askokcancel("Warning", ("The Merge HEM Runs application will "
                    + "delete from the original rungroup folder any summary files, "
                    + "Demographic Assessment results, and KMZ files, and place all merged files in that original folder. Select Ok to continue or Cancel "
                    + "to stop this operation.")) 
        if result:
            
            #---------- Adjust the GUI -------------------
            self.setGui4run()
            
            # Instantiate the merger
            merger = MergeHemRuns(self.origPath, self.newPath)
            
            # Run the merger in a concurrent thread
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(merger.PerformMerge)
            future.add_done_callback(self.finish_merge)
        else:
            messagebox.showinfo("Canceled", "HEM Merge operation was canceled")
            Logger.logMessage("HEM Merge operation was canceled\n")
            self.resetGui()
            

    def finish_merge(self, future):
        if future.exception():
            messagebox.showinfo("Finished", "HEM Merge completed with an error. Please see the log for details.")
            Logger.logMessage("\nHEM Merge completed with an error. Error is: \n"
                              + str(future.exception()))
        else:
            messagebox.showinfo("Finished", "HEM Merge has successfully completed.")
    
        self.resetGui()
        
    
    def setGui4run(self):
        
        # Indicate with green icon that Merge app is running
        self.titleLabel.configure(image=self.home.greenIcon)
        self.home.xchangeLabel.configure(image=self.home.greenIcon)

        # Disable select folders and run button
        self.fileLabel.configure(state='disabled')
        self.fileLabel.bind("<Button-1>", partial(self.disabled_message))
        self.step1_instructions.configure(state='disabled')
        self.step1_instructions.bind("<Button-1>", partial(self.disabled_message))
        self.fileLabel2.configure(state='disabled')
        self.fileLabel2.bind("<Button-1>", partial(self.disabled_message))
        self.step2_instructions.configure(state='disabled')
        self.step2_instructions.bind("<Button-1>", partial(self.disabled_message))
        self.run_button.configure(state='disabled')
        self.run_button.bind("<Button-1>", partial(self.disabled_message))
        
        #disable hem4 tab
        self.home.newrunLabel.bind("<Button-1>", partial(self.disabled_message))
        self.home.iconLabel.bind("<Button-1>", partial(self.disabled_message))
        
        # Make Log window active
        self.home.hem.lift()
        self.fix_config(self.home.liLabel, self.home.logLabel, self.home.current_button)
        self.lift_page(self.home.liLabel, self.home.logLabel, self.home.log, self.home.current_button)
        

    def resetGui(self):

        # Reenable select folder and run widgets
        self.titleLabel.configure(image=self.titleicon)
        self.home.xchangeLabel.configure(image=self.home.updateIcon)

        self.fileLabel.bind("<Button-1>", partial(self.origBrowse, self.step1_instructions))        
        self.fileLabel.configure(state='normal')
        self.step1_instructions.bind("<Button-1>", partial(self.origBrowse, self.step1_instructions))
        self.step1_instructions.configure(state='normal')
        self.step1_instructions['text'] = "Select folder containing the original HEM run results"

        self.fileLabel2.bind("<Button-1>", partial(self.newBrowse, self.step2_instructions))
        self.fileLabel2.configure(state='normal')
        self.step2_instructions.bind("<Button-1>", partial(self.newBrowse, self.step2_instructions))
        self.step2_instructions.configure(state='normal')
        self.step2_instructions['text'] = "Select folder containing the new HEM run results"

        self.run_button.configure(state='normal')
        self.run_button.bind("<Button-1>", self.run)
        
        #reenable hem4 tab
        self.home.newrunLabel.bind("<Button-1>", partial(self.home.lift_page, self.home.newrunLabel, self.home.iconLabel, self.home.hem, self.home.current_button))
        self.home.iconLabel.bind("<Button-1>", partial(self.home.lift_page, self.home.iconLabel, self.home.newrunLabel, self.home.hem, self.home.current_button))

        # # Make Merge window active
        # self.home.hem.lift()
        # self.fix_config(self.home.xchangeLabel, self.home.optionsLabel, self.home.current_button)
        # self.lift_page(self.home.xchangeLabel, self.home.optionsLabel, self.home.options, self.home.current_button)
        


    def lift_page(self, widget1, widget2, page, previous):
        """
        Function lifts page and changes button color to active,
        changes previous button color
        """
        try:
            widget1.configure(bg=self.tab_color)
            widget2.configure(bg=self.tab_color)

            if len(self.home.current_button) > 0:

                for i in self.home.current_button:
                    i.configure(bg=self.main_color)

            page.lift()
            self.home.current_button = [widget1, widget2]
            
        except Exception as e:

            print(e)
