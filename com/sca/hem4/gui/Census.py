
from com.sca.hem4.gui.Page import Page
import tkinter as tk
import PIL.Image
from PIL import ImageTk
from com.sca.hem4.gui.Styles import TITLE_FONT, TEXT_FONT, MAIN_COLOR
from functools import partial
from tkinter.filedialog import askopenfilename
from concurrent.futures import ThreadPoolExecutor
from com.sca.hem4.tools.CensusUpdater import CensusUpdater
from tkinter import messagebox
from com.sca.hem4.log.Logger import Logger
from com.sca.hem4.upload.CensusChanges import CensusChanges
from com.sca.hem4.upload.CensusDF import CensusDF


class Census(Page):
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.home = nav

        container = tk.Frame(self, bg=self.tab_color, bd=2)
        container.pack(side="top", fill="both", expand=True)

        self.s1 = tk.Frame(container, width=600, height=50, bg=self.tab_color)
        self.s2 = tk.Frame(container, width=600, height=50, bg=self.tab_color)
        self.s3 = tk.Frame(container, width=600, height=50, bg=self.tab_color)
        self.s4 = tk.Frame(container, width=600, height=50, bg=self.tab_color)
        self.s5 = tk.Frame(container, width=600, height=50, bg=self.tab_color)

        self.s1.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.s2.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.s3.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.s4.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.s5.grid(row=4, column=0, columnspan=2, sticky="nsew")

        self.tt = PIL.Image.open('images\icons8-settings-48-white.png').resize((30,30))
        self.tticon = self.add_margin(self.tt, 5, 0, 5, 0)
        self.titleicon = ImageTk.PhotoImage(self.tticon)
        self.titleLabel = tk.Label(self.s1, image=self.titleicon, bg=self.tab_color)
        self.titleLabel.image = self.titleicon # keep a reference!
        self.titleLabel.grid(row=1, column=0, padx=10, pady=10)

        title2 = tk.Label(self.s1, text="UPDATE CENSUS", font=TITLE_FONT, fg=MAIN_COLOR, bg=self.tab_color)
        title2.grid(row=1, column=1, padx=10, sticky='W', pady=10)

        fu = PIL.Image.open('images\icons8-folder-48.png').resize((30,30))
        ficon = self.add_margin(fu, 5, 0, 5, 0)
        fileicon = ImageTk.PhotoImage(ficon)
        self.fileLabel = tk.Label(self.s3, image=fileicon, bg=self.tab_color)
        self.fileLabel.image = fileicon # keep a reference!
        self.fileLabel.grid(row=0, column=0, padx=10)

        self.folder_select = tk.Label(self.s3, text="Please select a census update file:", font=TITLE_FONT, bg=self.tab_color, anchor="w")
        self.folder_select.grid(pady=10, padx=10, row=0, column=1)

        self.fileLabel.bind("<Enter>", partial(self.color_config, self.fileLabel, self.folder_select, self.s3, 'light grey'))
        self.fileLabel.bind("<Leave>", partial(self.color_config, self.fileLabel, self.folder_select, self.s3, self.tab_color))
        self.fileLabel.bind("<Button-1>", partial(self.uploadCensusUpdates))

        self.folder_select.bind("<Enter>", partial(self.color_config, self.folder_select, self.fileLabel, self.s3, 'light grey'))
        self.folder_select.bind("<Leave>", partial(self.color_config, self.folder_select, self.fileLabel, self.s3, self.tab_color))
        self.folder_select.bind("<Button-1>", partial(self.uploadCensusUpdates))

        ru = PIL.Image.open('images\icons8-update-48.png').resize((30,30))
        ricon = self.add_margin(ru, 5, 0, 5, 0)
        self.rileicon = ImageTk.PhotoImage(ricon)
        self.rileLabel = tk.Label(self.s4, image=self.rileicon, bg=self.tab_color)
        self.rileLabel.image = self.rileicon # keep a reference!
        self.rileLabel.grid(row=0, column=1, padx=10, sticky='E')

        self.run_button = tk.Label(self.s4, text="Update", font=TEXT_FONT, bg=self.tab_color)
        self.run_button.grid(row=0, column=2, padx=5, pady=10, sticky='E')

        self.run_button.bind("<Enter>", partial(self.color_config, self.run_button, self.rileLabel, self.s4, 'light grey'))
        self.run_button.bind("<Leave>", partial(self.color_config, self.run_button, self.rileLabel, self.s4, self.tab_color))
        self.run_button.bind("<Button-1>", self.update_census)

        self.rileLabel.bind("<Enter>", partial(self.color_config, self.rileLabel, self.run_button, self.s4, 'light grey'))
        self.rileLabel.bind("<Leave>", partial(self.color_config, self.rileLabel, self.run_button, self.s4, self.tab_color))
        self.rileLabel.bind("<Button-1>", self.update_census)

    def update_census(self, event):
        """
        Function creates thread for running HEM4 concurrently with tkinter GUI
        """

        # Make sure census change file has been uploaded
        try:
            self.censusUpdatePath

        except AttributeError:
            messagebox.showinfo("Update file not selected", "Please use the 'Select a census update file' button before using the UPDATE button")
            return

        else:

            # Indicate with green icon that updater is running
            self.titleLabel.configure(image=self.home.greenIcon)
            self.home.gearLabel.configure(image=self.home.greenIcon)
            
            # Disable select folder and run button
            self.folder_select.configure(state='disabled')
            self.folder_select.bind("<Button-1>", partial(self.disabled_message))
            self.fileLabel.configure(state='disabled')
            self.fileLabel.bind("<Button-1>", partial(self.disabled_message))
            self.run_button.configure(state='disabled')
            self.run_button.bind("<Button-1>", partial(self.disabled_message))
            self.rileLabel.configure(state='disabled')
            self.rileLabel.bind("<Button-1>", partial(self.disabled_message))
            
            #disable hem4 tab
            self.home.newrunLabel.bind("<Button-1>", partial(self.disabled_message))
            self.home.iconLabel.bind("<Button-1>", partial(self.disabled_message))
            
            # Make Log window active
            self.home.hem.lift()
            self.fix_config(self.home.liLabel, self.home.logLabel, self.home.current_button)
            self.lift_page(self.home.liLabel, self.home.logLabel, self.home.log, self.home.current_button)

            # Instantiate the updater which loads the Census data
            self.censusupdater = CensusUpdater(self.changeset_df)
            # Was the Census data uploaded?
            if self.censusupdater.census_df.empty:
                self.reset()
                return
            
            executor = ThreadPoolExecutor(max_workers=1)
    
            future = executor.submit(self.censusupdater.generateChanges)
            future.add_done_callback(self.finish_census_update)

    def reset(self):

        # Reenable select folder and run widgets
        self.folder_select.configure(state='normal')
        self.folder_select.bind("<Button-1>", partial(self.uploadCensusUpdates))
        self.fileLabel.configure(state='normal')
        self.fileLabel.bind("<Button-1>", partial(self.uploadCensusUpdates))
        self.run_button.configure(state='normal')
        self.run_button.bind("<Button-1>", self.update_census)
        self.rileLabel.configure(state='normal')
        self.rileLabel.bind("<Button-1>", self.update_census)
        self.folder_select['text'] = "Please select a census update file:"
        self.titleLabel.configure(image=self.titleicon)
        self.home.gearLabel.configure(image=self.home.gearLabel.image)
        
        #reenable hem4 tab
        self.home.newrunLabel.bind("<Button-1>", partial(self.home.lift_page, self.home.newrunLabel, self.home.iconLabel, self.home.hem, self.home.current_button))
        self.home.iconLabel.bind("<Button-1>", partial(self.home.lift_page, self.home.iconLabel, self.home.newrunLabel, self.home.hem, self.home.current_button))

        # Make Census Update window active
        self.home.hem.lift()
        self.fix_config(self.home.gearLabel, self.home.optionsLabel, self.home.current_button)
        self.lift_page(self.home.gearLabel, self.home.optionsLabel, self.home.options, self.home.current_button)


    def finish_census_update(self, future):

        # Reenable select folder and run widgets
        self.folder_select.configure(state='normal')
        self.folder_select.bind("<Button-1>", partial(self.uploadCensusUpdates))
        self.fileLabel.configure(state='normal')
        self.fileLabel.bind("<Button-1>", partial(self.uploadCensusUpdates))
        self.run_button.configure(state='normal')
        self.run_button.bind("<Button-1>", self.update_census)
        self.rileLabel.configure(state='normal')
        self.rileLabel.bind("<Button-1>", self.update_census)
        self.folder_select['text'] = "Please select a census update file:"
        self.titleLabel.configure(image=self.titleicon)
        self.home.gearLabel.configure(image=self.home.gearLabel.image)
        
        #reenable hem4 tab
        self.home.newrunLabel.bind("<Button-1>", partial(self.home.lift_page, self.home.newrunLabel, self.home.iconLabel, self.home.hem, self.home.current_button))
        self.home.iconLabel.bind("<Button-1>", partial(self.home.lift_page, self.home.iconLabel, self.home.newrunLabel, self.home.hem, self.home.current_button))

        messagebox.showinfo("Finished", "Census updater has completed.")
        
    def uploadCensusUpdates(self, event):

        # Get the update file        
        fullpath = self.openFile(askopenfilename())
        if not fullpath:
            return
        else:
            # try to load the file
            self.censusUpdatePath = fullpath
            Logger.logMessage("/nLoading the census change file...")
            censuschanges = CensusChanges(self.censusUpdatePath)
            self.changeset_df = censuschanges.dataframe
            if self.changeset_df.empty:
                return
            else:
                self.folder_select['text'] = fullpath.split("\\")[-1]        
            

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
