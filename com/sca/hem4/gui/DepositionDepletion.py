from com.sca.hem4.gui.Page import Page
import tkinter as tk
from PIL import ImageTk
import PIL.Image
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from com.sca.hem4.gui.Styles import TITLE_FONT


class DepositionDepletion(Page):
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.model = nav.model
        self.uploader = nav.uploader

        self.nav = nav

        self.dep_part_up = None
        self.dep_land_up = None
        self.dep_seasons_up = None

        # set text variables for labels

        # particle size input
        self.partlbl = tk.StringVar()
        self.partlbl.set("Please select Particle Size file:")

        # land file input
        self.landlbl = tk.StringVar()
        self.landlbl.set("Please select Land Use file:")

        # seasons file input
        self.seasonlbl = tk.StringVar()
        self.seasonlbl.set("Please select Month-to-Season Vegetation file:")

        # Frames for main inputs
        self.required_inputs = tk.Frame(self, width=600, bg=self.tab_color)
        self.required_inputs.pack(fill="both", expand=True, side="top")

        self.s1 = tk.Frame(self.required_inputs, width=600, height=50, bg=self.tab_color)
        self.s2 = tk.Frame(self.required_inputs, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s3 = tk.Frame(self.required_inputs, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s4 = tk.Frame(self.required_inputs, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s5 = tk.Frame(self.required_inputs, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s6 = tk.Frame(self.required_inputs, width=600, height=50, pady=5, padx=5, bg=self.tab_color)

        # grid layout for main inputs
        self.s1.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.s2.grid(row=1, column=0)
        self.s3.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        self.s4.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.s5.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.s6.grid(row=5, column=0, columnspan=2, sticky="nsew")

        self.required_inputs.grid_rowconfigure(8, weight=4)
        self.required_inputs.grid_columnconfigure(2, weight=1)

        self.s2.grid_propagate(0)

        self.tt = PIL.Image.open('images\icons8-add-column-48-white.png').resize((30,30))
        self.tticon = self.add_margin(self.tt, 5, 0, 5, 0)
        self.titleicon = ImageTk.PhotoImage(self.tticon)
        self.titleLabel = tk.Label(self.s1, image=self.titleicon, bg=self.tab_color)
        self.titleLabel.image = self.titleicon # keep a reference!
        self.titleLabel.grid(row=1, column=0, padx=10, pady=10)

        self.title = tk.Label(self.s1, font=TITLE_FONT, fg="white", bg=self.tab_color,
                              text="DEPOSITION & DEPLETION INPUTS")
        self.title.grid(row=1, column=1, sticky="W", pady=10, padx=10)

        # Setting up  directions text space
        self.add_instructions(self.s3, self.s3)

    def lift_tab(self):

        self.nav.run()

    def back_tab(self):

        if 'buoyant' in self.nav.model.dependencies or 'poly' in self.nav.model.dependencies or 'bldg_dw' in self.nav.model.dependencies or 'emisvar' in self.nav.model.dependencies:
            self.optional.lift()

        else:
            self.nav.lift()

    def uploadParticle(self, facilities, container, label, event):
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
                                          self.model.hapemis.dataframe, facilities)

            if self.model.partdep.dataframe.empty == False:

                # Update the UI
                [self.nav.nav.log.scr.insert(tk.INSERT, msg) for msg in self.model.partdep.log]
                #            container.configure(bg='light green')

                self.partlbl.set('')
                self.partlbl.set(fullpath.split("\\")[-1])

    def uploadLandUse(self, container, label, event):
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
                                          self.model.gasdryfacs)

            if self.model.landuse.dataframe.empty == False:


                # Update the UI
                [self.nav.nav.log.scr.insert(tk.INSERT, msg) for msg in self.model.landuse.log]
                #            container.configure(bg='light green')

                self.landlbl.set('')
                self.landlbl.set(fullpath.split("\\")[-1])

    def uploadSeasons(self, container, label, event):
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
                                          self.model.gasdryfacs)

            if self.model.seasons.dataframe.empty == False:


                # Update the UI
                [self.nav.nav.log.scr.insert(tk.INSERT, msg) for msg in self.model.seasons.log]
                #            container.configure(bg='light green')

                self.seasonlbl.set('')
                self.seasonlbl.set(fullpath.split("\\")[-1])
