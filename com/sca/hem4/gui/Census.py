
from com.sca.hem4.gui.Page import Page
import tkinter as tk
import PIL.Image
from PIL import ImageTk
from com.sca.hem4.gui.Styles import TITLE_FONT, TEXT_FONT
from functools import partial
from tkinter.filedialog import askopenfilename
from concurrent.futures import ThreadPoolExecutor
from com.sca.hem4.tools.CensusUpdater import CensusUpdater


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

        title2 = tk.Label(self.s1, text="REVISE CENSUS", font=TITLE_FONT, fg="white", bg=self.tab_color)
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
        rileicon = ImageTk.PhotoImage(ricon)
        rileLabel = tk.Label(self.s4, image=rileicon, bg=self.tab_color)
        rileLabel.image = rileicon # keep a reference!
        rileLabel.grid(row=0, column=1, padx=10, sticky='E')

        run_button = tk.Label(self.s4, text="Revise", font=TEXT_FONT, bg=self.tab_color)
        run_button.grid(row=0, column=2, padx=5, pady=10, sticky='E')

        run_button.bind("<Enter>", partial(self.color_config, run_button, rileLabel, self.s4, 'light grey'))
        run_button.bind("<Leave>", partial(self.color_config, run_button, rileLabel, self.s4, self.tab_color))
        run_button.bind("<Button-1>", self.update_census)

        rileLabel.bind("<Enter>", partial(self.color_config, rileLabel, run_button, self.s4, 'light grey'))
        rileLabel.bind("<Leave>", partial(self.color_config, rileLabel, run_button, self.s4, self.tab_color))
        rileLabel.bind("<Button-1>", self.update_census)

    def update_census(self, event):
        """
        Function creates thread for running HEM4 concurrently with tkinter GUI
        """

        #disable hem4 tab
        self.home.newrunLabel.bind("<Button-1>", partial(self.disabled_message))
        self.home.iconLabel.bind("<Button-1>", partial(self.disabled_message))


        executor = ThreadPoolExecutor(max_workers=1)

        future = executor.submit(self.censusupdater.update, self.censusUpdatePath)
        future.add_done_callback(self.update_census_finish)

    def update_census_finish(self, future):
        self.callbackQueue.put(self.finish_census_update)

    def finish_census_update(self):
        self.folder_select['text'] = "Please select a census update file:"

        #reenable hem4 tab
        self.home.newrunLabel.bind("<Button-1>", partial(self.home.lift_page, self.home.newrunLabel, self.home.iconLabel, self.home.hem, self.home.current_button))
        self.home.iconLabel.bind("<Button-1>", partial(self.home.lift_page, self.home.iconLabel, self.home.newrunLabel, self.home.hem, self.home.current_button))

    def uploadCensusUpdates(self, event):
        self.censusupdater = CensusUpdater()
        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.censusUpdatePath = fullpath
            self.folder_select['text'] = fullpath.split("\\")[-1]
