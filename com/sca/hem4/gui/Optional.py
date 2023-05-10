from com.sca.hem4.gui.Page import Page
from com.sca.hem4.gui.Styles import TITLE_FONT, MAIN_COLOR
import tkinter as tk
from PIL import ImageTk
import PIL.Image
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

class Optional(Page):
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.poly_up = None
        self.buoyant_up = None
        self.bldgdw_up = None
        self.ur = None

        #set text variables for input labels

        #user receptor
        self.urlbl = tk.StringVar()
        self.urlbl.set("Please select a User Receptors file:")

        #variation
        self.varlbl = tk.StringVar()
        self.varlbl.set("Please select an Emissions Variation file:")

        #buoyant line
        self.buoylbl = tk.StringVar()
        self.buoylbl.set("Please select associated Buoyant Line"+
                         " Parameters file:")

        #poly vertex
        self.polylbl = tk.StringVar()
        self.polylbl.set("Please select associated Polygon Vertex file:")

        #building downwash
        self.bldgdwlbl = tk.StringVar()
        self.bldgdwlbl.set("Please select associated Building Dimensions file:")

        self.model = nav.model
        self.uploader = nav.uploader
        self.nav = nav

        ##Frames for main inputs
        self.required_inputs = tk.Frame(self, width=600, bg=self.tab_color)
        self.required_inputs.pack(fill="both", expand=True, side="top")

        self.s1 = tk.Frame(self.required_inputs, width=600, height=50, bg=self.tab_color)
        self.s3 = tk.Frame(self.required_inputs, width=600, pady=5, padx=5, bg=self.tab_color)
        self.s4 = tk.Frame(self.required_inputs, width=600, pady=5, padx=5, bg=self.tab_color)
        self.s5 = tk.Frame(self.required_inputs, width=600, pady=5, padx=5, bg=self.tab_color)
        self.s6 = tk.Frame(self.required_inputs, width=600, pady=5, padx=5, bg=self.tab_color)
        self.s7 = tk.Frame(self.required_inputs, width=600, pady=5, padx=5, bg=self.tab_color)
        self.s8 = tk.Frame(self.required_inputs, width=600, pady=5, padx=5, bg=self.tab_color)
        self.s9 = tk.Frame(self.required_inputs, width=600, pady=5, padx=5, bg=self.tab_color)

        #grid layout for main inputs
        self.s1.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.s3.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        self.s8.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.s9.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.s4.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.s5.grid(row=5, column=0, columnspan=2, sticky="nsew")
        self.s6.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.s7.grid(row=7, column=0, columnspan=2, sticky="nsew")

        self.required_inputs.grid_rowconfigure(9, weight=1)
        self.required_inputs.grid_columnconfigure(2, weight=1)

        self.tt = PIL.Image.open('images\icons8-add-column-48-white.png').resize((30,30))
        self.tticon = self.add_margin(self.tt, 5, 0, 5, 0)
        self.titleicon = ImageTk.PhotoImage(self.tticon)
        self.titleLabel = tk.Label(self.s1, image=self.titleicon, bg=self.tab_color)
        self.titleLabel.image = self.titleicon # keep a reference!
        self.titleLabel.grid(row=1, column=0, padx=10, pady=10)


        self.title = tk.Label(self.s1, font=TITLE_FONT, fg=MAIN_COLOR, bg=self.tab_color,
                              text="ADDITIONAL INPUTS")
        self.title.grid(row=1, column=1, sticky="W", pady=10, padx=10)

        #%% Setting up  directions text space

        self.add_instructions(self.s3, self.s3)

    # %% Setting up each file upload space (includes browse button, and manual text entry for file path)

    def lift_tab(self):

        if 'particle size' in self.model.dependencies or 'land use' in self.model.dependencies or 'seasons' in self.model.dependencies:
            self.nav.depdeplt.lift()

        else:

            self.nav.run()

    def back_tab(self):

        self.nav.lift()

    def uploadPolyvertex(self, container, label, event):
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


            if self.model.multipoly.dataframe.empty == False:

                # Update the UI
                [self.nav.nav.log.scr.insert(tk.END, msg) for msg in self.model.multipoly.log]
                #            container.configure(bg='light green')

                self.polylbl.set('')
                self.polylbl.set(fullpath.split("\\")[-1])


    def uploadbuoyant(self, container, label, event):
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

            if self.model.multibuoy.dataframe.empty == False:


                # Update the UI
                [self.nav.nav.log.scr.insert(tk.END, msg) for msg in self.model.multibuoy.log]
                #            container.configure(bg='light green')

                self.buoylbl.set('')
                self.buoylbl.set(fullpath.split("\\")[-1])


    def uploadBuildingDownwash(self, container, label, event):
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
                                          self.model)


            if self.model.bldgdw.dataframe.empty == False:

                # Update the UI
                [self.nav.nav.log.scr.insert(tk.END, msg) for msg in self.model.bldgdw.log]
                #            container.configure(bg='light green')

                self.bldgdwlbl.set('')
                self.bldgdwlbl.set(fullpath.split("\\")[-1])



    def uploadUserReceptors(self, container, label, event):
        """
        Function for uploading user receptors
        """

        if self.model.faclist.dataframe is None:
            messagebox.showinfo("Facilities List Option File Missing",
                                "Please upload a Facilities List Options file before selecting"+
                                " a User Receptors file.")
            return

        fullpath = self.openFile(askopenfilename())
        if fullpath is not None:
            self.uploader.uploadDependent("user receptors", fullpath, self.model.faclist.dataframe)

            if self.model.ureceptr.dataframe.empty == False:


                self.model.model_optns['ureceptr'] = True
                # Update the UI
                [self.nav.nav.log.scr.insert(tk.END, msg) for msg in self.model.ureceptr.log]

                self.urlbl.set('')
                self.urlbl.set(fullpath.split("\\")[-1])
