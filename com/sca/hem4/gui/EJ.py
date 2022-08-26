import glob
import os
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from tkinter import messagebox

from com.sca.hem4.ej.EnvironmentalJustice import EnvironmentalJustice
from com.sca.hem4.ej.ReportWriter import ReportWriter
from com.sca.hem4.ej.data.ACSCountyTract import ACSCountyTract
from com.sca.hem4.ej.data.ACSDataset import ACSDataset
from com.sca.hem4.ej.data.DataModel import DataModel
from com.sca.hem4.ej.summary.FacilitySummary import FacilitySummary
from com.sca.hem4.gui.EntryWithPlaceholder import EntryWithPlaceholder
from com.sca.hem4.gui.Page import Page
import tkinter as tk
import tkinter.ttk as ttk
from com.sca.hem4.gui.Styles import TEXT_FONT, SMALL_TEXT_FONT, TITLE_FONT, MAIN_COLOR, HIGHLIGHT_COLOR, SUBTITLE_FONT
import PIL.Image
from PIL import ImageTk
from functools import partial

from com.sca.hem4.log import Logger
from com.sca.hem4.upload.MetLib import MetLib
from com.sca.hem4.writer.csv.MirHIAllReceptors import *
from decimal import ROUND_HALF_UP, Decimal, getcontext
from com.sca.hem4.writer.excel.summary.AltRecAwareSummary import AltRecAwareSummary

# The GUI portion of the EJ functionality in HEM4. This class manages the various dialogs and options needed
# to kick off a run of the EJ reporting tool. Its main entry into the code that actually performs the report
# creation is the EnvironmentalJustice class from the ej package.
class EJ(Page):
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        self.nav = nav

        # Report combinations (radius, cancer risk, HI risk). The GUI allows up to 4 at once.
        self.combinations = {}
        self.radios = {}

        # The data structures that correspond to combinations.
        self.run_configs = None
        self.next_config = 1
        self.fullpath = None

        self.toshis = {'Deve':'Developmental', 'Endo':'Endocrine', 'Hemo':'Hemotological', 'Immu':'Immunological',
                       'Kidn':'Kidney', 'Live':'Liver', 'Neur':'Neurological', 'Ocul':'Ocular', 'Repr':'Reproductive',
                       'Resp':'Respiratory', 'Skel':'Skeletal', 'Sple':'Spleen', 'Thyr':'Thyroid', 'Whol':'Whole Body'
        }
        self.acs_df = None
        self.levels_df = None
        self.all_receptors_df = None


        self.container = tk.Frame(self, bg=self.tab_color, bd=2)
        self.container.pack(side="top", fill="both", expand=True)

        # Create grid
        self.title_frame = tk.Frame(self.container, height=80, bg=self.tab_color)
        self.folder_frame = tk.Frame(self.container, height=120, pady=1, padx=5, bg=self.tab_color)
        self.category_frame = tk.Frame(self.container, height=200, pady=1, padx=5, bg=self.tab_color)
        self.parameters_frame = tk.Frame(self.container, height=200, pady=1, padx=5, bg=self.tab_color)
        self.run_frame = tk.Frame(self.container, height=100, pady=1, padx=5, bg=self.tab_color)

        self.title_frame.grid(row=1, columnspan=5, sticky="nsew")
        self.folder_frame.grid(row=2, columnspan=5, sticky="nsew")
        self.category_frame.grid(row=3, columnspan=5, sticky="nsew")
        self.parameters_frame.grid(row=4, columnspan=5, sticky="nsew")
        self.run_frame.grid(row=6, columnspan=5, sticky="e")

                               
        # Create a folder dialog button
        title_image = PIL.Image.open('images\icons8-people-48.png').resize((30,30))
        tticon = self.add_margin(title_image, 5, 0, 5, 0)
        titleicon = ImageTk.PhotoImage(tticon)
        self.titleLabel = tk.Label(self.title_frame, image=titleicon, bg=self.tab_color)
        self.titleLabel.image = titleicon # keep a reference!
        self.titleLabel.grid(row=1, column=0, padx=10, pady=1)
        title = tk.Label(self.title_frame, text="CREATE COMMUNITY ASSESSMENT REPORTS", font=TITLE_FONT,
                         fg=MAIN_COLOR, bg=self.tab_color, anchor="w")
        title.grid(row=1, column=1, pady=2, padx=10, sticky="w")
        subtitle = tk.Label(self.title_frame, text="Note: The Community Assessment module may be used with HEM4 runs based on U.S. Census Block receptors only.", 
                            font=SMALL_TEXT_FONT, bg=self.tab_color, anchor="w", wraplength=600,
                            justify="left")
        subtitle.grid(row=2, column=1, pady=2, padx=10, sticky="w")

        # First step - choose an output folder
        self.step1 = tk.Label(self.folder_frame,
                              text="1.", font=SMALL_TEXT_FONT, bg=self.tab_color, anchor="w")
        self.step1.grid(pady=10, padx=10, row=1, column=0)

        fu = PIL.Image.open('images\icons8-folder-48.png').resize((30,30))
        ficon = self.add_margin(fu, 5, 0, 5, 0)
        fileicon = ImageTk.PhotoImage(ficon)
        self.fileLabel = tk.Label(self.folder_frame, image=fileicon, bg=self.tab_color)
        self.fileLabel.image = fileicon # keep a reference!
        self.fileLabel.grid(row=1, column=1, padx=10)

        self.step1_instructions = tk.Label(self.folder_frame,
                                      text="Select output folder", font=SMALL_TEXT_FONT, bg=self.tab_color, anchor="w")
        self.step1_instructions.grid(pady=10, padx=10, row=1, column=2)
        self.fileLabel.bind("<Button-1>", partial(self.browse, self.step1_instructions))
        self.step1_instructions.bind("<Button-1>", partial(self.browse, self.step1_instructions))

        # Second step - choose category name and prefix
        self.step2 = tk.Label(self.category_frame,
                              text="2.", font=SMALL_TEXT_FONT, bg=self.tab_color, anchor="w")
        self.step2.grid(pady=10, padx=10, row=1, column=0)

        self.step2_instructions = tk.Label(self.category_frame, font=SMALL_TEXT_FONT, bg=self.tab_color,
                              text="Enter a run group name and prefix.")
        self.step2_instructions.grid(row=1, column=1, padx=5, sticky="W", columnspan=2)

        self.name_lbl = tk.Label(self.category_frame, font=SMALL_TEXT_FONT, bg=self.tab_color, text="Name:")
        self.name_lbl.grid(row=2, column=1, padx=5, sticky="W")

        self.category_name = EntryWithPlaceholder(self.category_frame, placeholder="ex: Primary Copper Manufacturing")
        self.category_name["width"] = 36
        self.category_name.grid(row=2, column=2, sticky="W")

        self.prefix_lbl = tk.Label(self.category_frame, font=SMALL_TEXT_FONT, bg=self.tab_color, text="Prefix:")
        self.prefix_lbl.grid(row=3, column=1, padx=5, sticky="W")
        self.category_prefix = EntryWithPlaceholder(self.category_frame, placeholder="ex: PCM")
        self.category_prefix["width"] = 8
        self.category_prefix.grid(row=3, column=2, sticky="W")

        # Third step - configure report combinations
        self.step3 = tk.Label(self.parameters_frame, text="3.", font=SMALL_TEXT_FONT, bg=self.tab_color, anchor="w")
        self.step3.grid(pady=10, padx=10, row=1, column=0)

        step3_text = "Choose type of impact (cancer or noncancer) for basis of demographics analysis, the radius " +\
                     "around each facility to include, and the impact level at which population percentages will " +\
                     "be calculated. Note: proximity statistics will be included at your specified radius."
        self.step3_instructions = tk.Label(self.parameters_frame, font=SMALL_TEXT_FONT, bg=self.tab_color, wraplength=650,
                                           justify="left", text=step3_text)
        self.step3_instructions.grid(row=1, column=1, padx=5, sticky="W", columnspan=4, rowspan=3)

        self.add_config(initYN="Y", radius=50, cancer_risk=1, hi_risk=1)
        self.create_add_config()

        ru = PIL.Image.open('images\icons8-create-48.png').resize((30,30))
        ricon = self.add_margin(ru, 5, 0, 5, 0)
        rileicon = ImageTk.PhotoImage(ricon)
        rileLabel = tk.Label(self.run_frame, image=rileicon, bg=self.tab_color)
        rileLabel.image = rileicon # keep a reference!
        rileLabel.grid(row=1, column=1, padx=0, pady=20, sticky='E')

        run_button = tk.Label(self.run_frame, text="Run Reports", font=TEXT_FONT, bg=self.tab_color)
        run_button.grid(row=1, column=2, padx=20, pady=20, sticky='E')

        run_button.bind("<Enter>", partial(self.color_config, run_button, rileLabel, self.run_frame, 'light grey'))
        run_button.bind("<Leave>", partial(self.color_config, run_button, rileLabel, self.run_frame, self.tab_color))
        run_button.bind("<Button-1>", self.run_reports)

        rileLabel.bind("<Enter>", partial(self.color_config, rileLabel, run_button, self.run_frame, 'light grey'))
        rileLabel.bind("<Leave>", partial(self.color_config, rileLabel, run_button, self.run_frame, self.tab_color))
        rileLabel.bind("<Button-1>", self.run_reports)

        
        
    # Reset the GUI to its original (default) state.
    def reset(self):
        self.step1_instructions["text"] = "Select output folder"
        self.fullpath = None

        self.category_name.put_placeholder()
        self.category_prefix.put_placeholder()

        for frame in self.combinations.values():
            frame.grid_forget()

        self.combinations = {}

        self.add_config(initYN="Y", radius=50, cancer_risk=1, hi_risk=1)

        if self.add_config_btn is None:
            self.create_add_config()

        self.nav.peopleLabel.configure(image=self.nav.ejIcon)
        self.titleLabel.configure(image=self.nav.ejIcon)

    # The folder browse handler.
    def browse(self, icon, event):
        self.fullpath = tk.filedialog.askdirectory()
        if not self.fullpath:
            return
        
        # Make sure the folder selected is not for an Alternate Receptor run group.
        # EJ cannot be run on that because there is no census block id to link to.
        altrecfinder = AltRecAwareSummary()
        altrec = altrecfinder.determineAltRec(self.fullpath)
        if altrec == 'Y':
            messagebox.showinfo('Cannot run Community Assessment on this folder',
                                'The folder selected for a Community Assessment contains HEM4 outputs that ' +
                                'use Alternate Receptors. These cannot be used with the Community Assessment Tool.')
            return
        
        icon["text"] = self.fullpath.split("/")[-1]

        # We have to inspect the input faclist once we know the path in order to determine
        # the minimum max_dist value that HEM4 used across all facilities during modeling.
        # This value will be an upper bound on the radius choice in the EJ GUI.
        faclist_path = os.path.join(self.fullpath, "Inputs/faclist.xlsx")
        faclist = FacilityList(faclist_path, metlib=MetLib())
        faclist.createDataframe()
        faclist_df = faclist.dataframe
        print(str(len(faclist_df)))

        faclist_df[max_dist] = faclist_df[max_dist].fillna(50000)

        self.min_max_dist = faclist_df[max_dist].min()


    # Event handlers for porting instructions
    def add_instructions(self, placeholder1, placeholder2):

        # Dynamic instructions place holder
        global instruction_instance
        self.instruction_instance = tk.StringVar(placeholder1)
        self.instruction_instance.set(" ")
        self.dynamic_inst = tk.Label(placeholder2, wraplength=600, font=TEXT_FONT, padx=20, bg=self.tab_color)
        self.dynamic_inst.config(height=4)

        self.dynamic_inst["textvariable"] = self.instruction_instance
        self.dynamic_inst.grid(row=11, column=0)


    def browse_inst(self, location):
        """
        Function looks up text file with instructions for specified input
        browse buttons
        """
        global instruction_instance
        self.read_inst = open(location, 'r')
        self.instruction_instance.set(self.read_inst.read())


    def color_config(self, widget1, widget2, container, color, event):

        widget1.configure(bg=color)
        widget2.configure(bg=color)
        container.configure(bg=color)



    # Note that when a combination is removed, the add config button may have to reappear, depending on how many are
    # left.
    def remove_config(self, config):

        if len(self.combinations) > 1:
            self.combinations[config].destroy()
            del self.combinations[config]

            if self.add_config_btn is None:
                self.create_add_config()

            # Sort all remaining rows and re-grid them one at a time in order to preserve the
            # row numbering
            sorted_configs = {k: self.combinations[k] for k in sorted(self.combinations)}
            new_frame_row = 1
            for config in sorted_configs:
                self.combinations[config].grid(row=new_frame_row+4, columnspan=5, padx=50, sticky="nsew")
                new_frame_row += 1
        else:
            messagebox.showinfo('Error', "You must have at least one configuration.")

    # Create the button that allows the user to add another config
    def create_add_config(self):
        self.add_config_btn = tk.Button(self.parameters_frame, text="Add combination", bg='lightgrey', relief='solid',
                                        borderwidth=1, command=self.add_next_config, font=SMALL_TEXT_FONT)
        self.add_config_btn.grid(row=12, column=1, sticky='W', padx=10, pady=5)

    # Add next config in response to user pressing add config button, and manage the availability of the button.
    def add_next_config(self):
        self.add_config(initYN="N", radius=None, cancer_risk=None, hi_risk=None)

        num_configs = len(self.combinations)
        if num_configs == 4:
            self.add_config_btn.grid_forget()
            self.add_config_btn = None

    # Create a new combination with default values.
    def add_config(self, initYN, radius, cancer_risk, hi_risk):
        num_configs = len(self.combinations)
        config = self.next_config
        frame_color = 'lightyellow'
        frame_name = 'frame' + str(config)
        new_frame = tk.Frame(self.parameters_frame, height=100, pady=5, padx=5, bg=frame_color,
                             highlightbackground="grey", highlightthickness=1, name=frame_name)

        frame_row = (num_configs%4)+5
        new_frame.grid(row=frame_row, column=0, columnspan=5, padx=50, sticky="nsew")
        self.combinations[config] = new_frame

        starting_row = 2
        config_lbl = tk.Label(new_frame, font=SMALL_TEXT_FONT, bg=frame_color,
                                   text="Combination:")
        config_lbl.grid(row=starting_row, column=1, padx=10, sticky="W")

        step3a = tk.Label(new_frame, font=SMALL_TEXT_FONT, bg=frame_color,
                               text="Radius (km)")
        step3a.grid(row=starting_row, column=2, padx=5, pady=2, sticky="SE")
        radius_num = EntryWithPlaceholder(new_frame, placeholder="<= 50", name="radius")
        radius_num["width"] = 8

        if radius is not None:
            radius_num.set_value(radius)
        radius_num.grid(row=starting_row, column=3, pady=3, sticky="SW")

        risk_num = EntryWithPlaceholder(new_frame, placeholder="(1-300)", name="cancer_risk")
        risk_num["width"] = 8

        self.radios[frame_name] = tk.IntVar()
        self.radios[frame_name].set(0)
        cancer_radio = tk.Radiobutton(new_frame, text="Cancer Risk Level (in a million)      >=", width=26,
                                      bg=frame_color,font=SMALL_TEXT_FONT, variable=self.radios[frame_name],
                                      name="cancer_radio", command=partial(self.handle_radio, new_frame), value=0)
        cancer_radio.grid(row=starting_row+1, column=2, padx=5, pady=0, sticky="NE")

        if cancer_risk is not None:
            risk_num.set_value(cancer_risk)
        risk_num.grid(row=starting_row+1, column=3, pady=3, sticky="NW")

        hi_radio = tk.Radiobutton(new_frame, text="Noncancer Hazard Index Level         >", width=26,
                                  bg=frame_color, font=SMALL_TEXT_FONT, variable=self.radios[frame_name],
                                  command=partial(self.handle_radio, new_frame), name="hi_radio", value=1)
        hi_radio.grid(row=starting_row+2, column=2, padx=5, pady=0, sticky="NE")

        hi_risk_num = EntryWithPlaceholder(new_frame, placeholder="(1-10)", name="hi_risk")
        hi_risk_num["width"] = 8
        if hi_risk is not None:
            hi_risk_num.set_value(hi_risk)
        hi_risk_num.grid(row=starting_row+2, column=3, pady=3, sticky="NW")

        hi_risk_num['state'] = 'disabled'
        hi_radio['fg'] = 'lightgrey'

        if initYN == "N":
            remove_btn = tk.Button(new_frame, text="Remove", bg='lightgrey', relief='solid', borderwidth=1,
                                  command=partial(self.remove_config, config), font=SMALL_TEXT_FONT)
            remove_btn.grid(row=starting_row+1, column=4, sticky='E', padx=10)

        self.next_config += 1

    # Handler for the cancer / HI radio button choice.
    def handle_radio(self, frame):
        frame_name = frame.winfo_name()
        cancer_radio = frame.nametowidget("cancer_radio")
        cancer_risk = frame.nametowidget("cancer_risk")
        hi_radio = frame.nametowidget("hi_radio")
        hi_risk = frame.nametowidget("hi_risk")

        if self.radios[frame_name].get() == 0:
            cancer_risk['state'] = 'normal'
            hi_risk['state'] = 'disabled'
            cancer_radio['fg'] = 'black'
            hi_radio['fg'] = 'lightgrey'
        else:
            cancer_risk['state'] = 'disabled'
            hi_risk['state'] = 'normal'
            cancer_radio['fg'] = 'lightgrey'
            hi_radio['fg'] = 'black'

    # Ensure all options are valid before proceeding to run reports.
    def verify_options(self):

        self.run_configs = {}

        if self.fullpath is None:
            messagebox.showinfo('Error', "Please select a HEM4 output folder.")
            return False

        if self.category_name.get_text_value() == '':
            messagebox.showinfo('Error', "Please specify a run group name.")
            return False

        if self.category_prefix.get_text_value() == '':
            messagebox.showinfo('Error', "Please specify a run group prefix.")
            return False

        for c in self.combinations.values():
            radius_value = c.nametowidget("radius").get_text_value()

            cancer_risk = c.nametowidget("cancer_risk")
            cancer_risk_value = cancer_risk.get_text_value()
            hi_risk = c.nametowidget("hi_risk")
            hi_risk_value = hi_risk.get_text_value()

            cancer_selected = cancer_risk["state"] == "normal"

            if radius_value == "" or (cancer_selected and cancer_risk_value == "") or \
                (not cancer_selected and hi_risk_value == ""):
                messagebox.showinfo('Error', "Please ensure all run combinations contain a value for radius and" +
                                    " the selected risk threshold.")
                return False

            try:
                radius_value = float(radius_value)
            except ValueError:
                messagebox.showinfo('Error', "Please ensure all radius values are numbers.")
                return False

            if radius_value < 1 or radius_value > 50:
                messagebox.showinfo('Error', "Please ensure all radius values satisfy 1 <= radius <= 50.")
                return False

            min_max_dist_km = int(self.min_max_dist / 1000)
            if radius_value > min_max_dist_km:
                messagebox.showinfo('Error', "The selected HEM4 output folder included a facility run at max dist = " +
                                    str(min_max_dist_km) + " km. Please ensure all radii are <= this value.")
                return False

            if cancer_selected:
                try:
                    cancer_risk_value = int(cancer_risk_value)
                    hi_risk_value = 1
                except ValueError:
                    messagebox.showinfo('Error', "Please ensure all cancer risk values are one of the following: " +
                                        "[1, 5, 10, 20, 30, 40, 50, 100, 200, 300]")
                    return False

                if cancer_risk_value not in [1, 5, 10, 20, 30, 40, 50, 100, 200, 300]:
                    messagebox.showinfo('Error', "Please ensure all cancer risk values are one of the following: " +
                                        "[1, 5, 10, 20, 30, 40, 50, 100, 200, 300]")
                    return False

            if not cancer_selected:
                try:
                    hi_risk_value = int(hi_risk_value)
                    cancer_risk_value = 1
                except ValueError:
                    messagebox.showinfo('Error', "Please ensure all HI risk values are one of the following: " +
                                        "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]")
                    return False

                if hi_risk_value not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                    messagebox.showinfo('Error', "Please ensure all HI risk values are one of the following: " +
                                        "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]")
                    return False

            existing = len(self.run_configs)
            self.run_configs[existing] = {'radius': radius_value, 'cancer_risk': cancer_risk_value,
                                          'hi_risk': hi_risk_value, 'cancer_selected': cancer_selected}

            self.run_configs[existing]['toshis'] = []

        return True

    # Kick off creation of reports on a new thread.
    def run_reports(self, event):
        # Verify all options ok
        options_ok = self.verify_options()

        # Launch the runner
        if options_ok:

            existing = len(self.run_configs)
            Logger.logMessage("Running HEM4 Environmental Justice reporting tool...")
            Logger.logMessage("Ready to run " + str(existing) + " run combinations.")

            self.nav.peopleLabel.configure(image=self.nav.greenIcon)
            self.titleLabel.configure(image=self.nav.greenIcon)

            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(self.create_reports)

    # Load all needed data sets and create an instance of EnvironmentalJustice so that we can
    # create reports.
    def create_reports(self):

        # First, load the ACS datasets needed for analysis (if they haven't already been loaded...)
        Logger.logMessage("Loading ACS data...")
        try:
            if self.acs_df is None:
                acs = ACSDataset(path="resources/acs.csv")
                self.acs_df = acs.dataframe

            if self.levels_df is None:
                levels = ACSCountyTract(path="resources/acs-levels.csv")
                self.levels_df = levels.dataframe
        except FileNotFoundError:
            messagebox.showinfo("Missing files",
                                "Unable to find required ACS data. Please check your HEM4 resources folder and " +
                                "try again.")
            return

        # Next, create (if doesn't exist) an all receptors file...
        all_receptors = MirHIAllReceptors(targetDir=self.fullpath)
        Logger.logMessage("Loading MIR HI All Receptors data...")
        try:
            self.all_receptors_df = all_receptors.createDataframe()
        except FileNotFoundError:
            Logger.logMessage("...creating MIR HI All Receptors data...")
            all_receptors.write()
            self.all_receptors_df = all_receptors.dataframe

        Logger.logMessage("MIR HI All Receptors dataset contains " + str(len(self.all_receptors_df)) + " records.")

        # Next, create an ej output directory if it doesn't already exist
        output_dir = os.path.join(self.fullpath, "ej")
        if not (os.path.exists(output_dir) or os.path.isdir(output_dir)):
            Logger.logMessage("Creating ej directory for results...")
            os.mkdir(output_dir)

        # Next, get the max risk and HI so that we can assign a distance to the block summary chronic datasets
        self.basepath = os.path.basename(os.path.normpath(self.fullpath))
        maxRiskAndHI = FacilityMaxRiskandHI(targetDir=self.fullpath,
                                            filenameOverride=self.basepath + "_facility_max_risk_and_hi.xlsx")

        try:
            maxRiskAndHI_df = maxRiskAndHI.createDataframe()
        except FileNotFoundError as e:
            Logger.logMessage("Couldn't find max risk file. Aborting...")
            messagebox.showinfo("File Not Found", "Please check the output folder for a properly named Facility Max Risk and HI file.")
            self.reset()
            return

        # Next, compile a list of all facility folders in the output folder (which will be used when we create
        # reports for each facility individually.)
        facilities = Directory.find_facilities(self.fullpath)

        # Initialize the class-level data storage for all facility summary workbooks and sheets
        ReportWriter.init_facility_summaries()
        FacilitySummary.init_sheets()

        # Finally, create reports for each requested combination of parameters
        config_num = 1
        for config in self.run_configs.values():
            Logger.logMessage("Creating EJ reports for combination #" + str(config_num))

            # Determine if this config was for cancer or HI
            cancer_selected = config["cancer_selected"]

            # Filter out MIR HI records that are outside the requested radius
            # Note the km to m conversion here!
            maxdist = config["radius"] * 1000

            filtered_mir_hi_df = self.all_receptors_df.query('distance <= @maxdist').copy()
            Logger.logMessage("Filtered MIR HI All Receptors dataset (radius = " + str(maxdist) + ") contains " +
                              str(len(filtered_mir_hi_df)) + " records.")

            # Infer which TOSHIs to include from the filtered all receptors file
            # should be of this form: {'Deve':'Developmental', 'Neur':'Neurological', ...}
            toshis = {} if cancer_selected else self.choose_toshis(filtered_mir_hi_df)

            try:
                ej = EnvironmentalJustice(mir_rec_df=filtered_mir_hi_df, acs_df=self.acs_df, levels_df=self.levels_df,
                                          outputdir=output_dir, source_cat_name=self.category_name.get_text_value(),
                                          source_cat_prefix=self.category_prefix.get_text_value(),
                                          radius=config["radius"], requested_toshis=toshis,
                                          cancer_risk_threshold=config["cancer_risk"],
                                          hi_risk_threshold=config["hi_risk"])

                # We will create -either- the cancer or HI reports but not both.
                ej.create_cancer_reports() if cancer_selected else ej.create_hi_reports()
                ej.create_facility_summaries(cancer_selected=cancer_selected)
            except BaseException as e:
                Logger.logMessage(e)

            Logger.logMessage("Creating facility specific reports...")
            for facilityId in facilities:
                Logger.logMessage(facilityId + "...")

                fac_path = os.path.join(self.fullpath, facilityId)

                # Use the Block Summary Chronic file instead of the MIR HI All receptors files to obtain risk values
                blockSummaryChronic = BlockSummaryChronic(targetDir=fac_path, facilityId=facilityId)
                bsc_df = blockSummaryChronic.createDataframe()

                # Filter out zero population blocks
                bsc_df = bsc_df[bsc_df['population'] != 0]

                # add a distance column
                maxrisk_df = maxRiskAndHI_df.loc[maxRiskAndHI_df['Facil_id'] == facilityId]
                center_lat = maxrisk_df.iloc[0]['fac_center_latitude']
                center_lon = maxrisk_df.iloc[0]['fac_center_longitude']
                ceny, cenx, zone, hemi, epsg = UTM.ll2utm(center_lat, center_lon)
                blkcoors = np.array(tuple(zip(bsc_df.lon, bsc_df.lat)))
                bsc_df[distance] = haversineDistance(blkcoors, center_lon, center_lat)
                
                # add a rounded mir column
                try:
                    bsc_df['mir_rounded'] = bsc_df['mir'].apply(DataModel.round_to_sigfig, 1)
                except BaseException as e:
                    Logger.logMessage(e)

                filtered_bsc_df = bsc_df.query('distance <= @maxdist').copy()
                Logger.logMessage("Filtered BlockSummaryChronic dataset (radius = " + str(maxdist) + ") contains " +
                                  str(len(filtered_bsc_df)) + " records.")

                fac_output_dir = os.path.join(output_dir, facilityId)
                if not (os.path.exists(fac_output_dir) or os.path.isdir(fac_output_dir)):
                    Logger.logMessage("Creating ej subdirectory for facility results...")
                    os.mkdir(fac_output_dir)

                try:
                    fac_ej = EnvironmentalJustice(facility=facilityId, mir_rec_df=filtered_bsc_df, acs_df=self.acs_df,
                                                  levels_df=self.levels_df, outputdir=fac_output_dir,
                                                  source_cat_name=self.category_name.get_text_value(),
                                                  source_cat_prefix=self.category_prefix.get_text_value(),
                                                  radius=config["radius"], requested_toshis=toshis,
                                                  cancer_risk_threshold=config["cancer_risk"],
                                                  hi_risk_threshold=config["hi_risk"])

                    # We will create -either- the cancer or HI reports but not both.
                    fac_ej.create_cancer_reports() if cancer_selected else fac_ej.create_hi_reports()
                    fac_ej.add_facility_summaries(run_group_data_model=ej.data_model, cancer_selected=cancer_selected)
                except BaseException as e:
                    traceback.print_exc()

            config_num += 1

        ej.close_facility_summaries()

        messagebox.showinfo("Community Assessment Reports Finished", "Please check the output folder for reports.")

        ej_directory = os.path.join(self.fullpath, "ej")
        next_log_name = self.find_next_log_name(ej_directory)
        Logger.archiveLog(run_dir=ej_directory, filename_override=next_log_name)
        Logger.initializeLog()

        self.reset()

    def find_next_log_name(self, directory):
        logfiles = glob.glob(directory + "/hem4*.log")
        if len(logfiles) == 0:
            return "hem4.log"

        logfiles.sort()
        most_recent = logfiles[-1]
        filename_no_extension = os.path.splitext(most_recent)[0]

        # Does the filename already have a digit extender?
        m = re.search(r'hem4_(\d+)$', filename_no_extension)
        if m is None:
            return filename_no_extension + "_1.log"
        else:
            part = int(m.group(1)) + 1
            filename_no_extension = re.sub(r"hem4_\d+$", "hem4_%s" % part, filename_no_extension)
            return filename_no_extension + ".log"

    # The method that automatically selects TOSHIs to report on based on a heuristic in the risk data.
    def choose_toshis(self, df):
        chosen = {}

        toshis = {hi_resp:'Resp', hi_live:'Live', hi_neur:'Neur', hi_deve:'Deve', hi_repr:'Repr', hi_kidn:'Kidn',
                  hi_ocul:'Ocul', hi_endo:'Endo', hi_hema:'Hemo', hi_immu:'Immu', hi_skel:'Skel', hi_sple:'Sple',
                  hi_thyr:'Thyr', hi_whol:'Whol'}

        max_value = 0
        max_toshi = None
        for toshi in toshis:

            # Keep track of the max in case we need to fall back on it
            max = df[toshi].max()
            if max > max_value:
                max_value = max
                max_toshi = toshi

            df_new = df[df[toshi] >= 1.5]
            if len(df_new) > 0:
                prefix = toshis[toshi]
                chosen[prefix] = self.toshis[prefix]

        # Fall back on the max TOSHI if none met the default threshold
        if len(chosen) == 0:
            prefix = toshis[max_toshi]
            chosen[prefix] = self.toshis[prefix]

        Logger.logMessage("TOSHIs chosen: ")
        Logger.logMessage(', '.join(list(chosen.values())))

        return chosen
