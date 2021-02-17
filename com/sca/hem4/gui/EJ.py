import os
from concurrent.futures.thread import ThreadPoolExecutor
from tkinter import messagebox

from com.sca.hem4.ej.EnvironmentalJustice import EnvironmentalJustice
from com.sca.hem4.ej.data.ACSCountyTract import ACSCountyTract
from com.sca.hem4.ej.data.ACSDataset import ACSDataset
from com.sca.hem4.gui.EntryWithPlaceholder import EntryWithPlaceholder
from com.sca.hem4.gui.Page import Page
import tkinter as tk
import tkinter.ttk as ttk
from com.sca.hem4.gui.Styles import TEXT_FONT, SMALL_TEXT_FONT, TITLE_FONT, MAIN_COLOR
import PIL.Image
from PIL import ImageTk
from functools import partial

from com.sca.hem4.log import Logger
from com.sca.hem4.writer.csv.MirHIAllReceptors import *


class EJ(Page):
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.nav = nav
        self.combinations = {}
        self.radios = {}
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

        # create grid
        self.title_frame = tk.Frame(self.container, height=100, bg=self.tab_color)
        self.folder_frame = tk.Frame(self.container, height=150, pady=5, padx=5, bg=self.tab_color)
        self.category_frame = tk.Frame(self.container, height=200, pady=5, padx=5, bg=self.tab_color)
        self.parameters_frame = tk.Frame(self.container, height=200, pady=5, padx=5, bg=self.tab_color)
        self.run_frame = tk.Frame(self.container, height=100, pady=5, padx=5, bg=self.tab_color)

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
        self.titleLabel.grid(row=1, column=0, padx=10, pady=10)
        title = tk.Label(self.title_frame, text="CREATE ENVIRONMENTAL JUSTICE REPORTS", font=TITLE_FONT,
                         fg=MAIN_COLOR, bg=self.tab_color, anchor="w")
        title.grid(row=1, column=1, pady=10, padx=10)

        # First step - choose an output folder
        self.step1 = tk.Label(self.folder_frame,
                              text="1.", font=TEXT_FONT, bg=self.tab_color, anchor="w")
        self.step1.grid(pady=10, padx=10, row=1, column=0)

        fu = PIL.Image.open('images\icons8-folder-48.png').resize((30,30))
        ficon = self.add_margin(fu, 5, 0, 5, 0)
        fileicon = ImageTk.PhotoImage(ficon)
        self.fileLabel = tk.Label(self.folder_frame, image=fileicon, bg=self.tab_color)
        self.fileLabel.image = fileicon # keep a reference!
        self.fileLabel.grid(row=1, column=1, padx=10)

        self.step1_instructions = tk.Label(self.folder_frame,
                                      text="Select output folder", font=TEXT_FONT, bg=self.tab_color, anchor="w")
        self.step1_instructions.grid(pady=10, padx=10, row=1, column=2)
        self.fileLabel.bind("<Button-1>", partial(self.browse, self.step1_instructions))
        self.step1_instructions.bind("<Button-1>", partial(self.browse, self.step1_instructions))

        # Second step - choose category name and prefix
        self.step2 = tk.Label(self.category_frame,
                              text="2.", font=TEXT_FONT, bg=self.tab_color, anchor="w")
        self.step2.grid(pady=10, padx=10, row=1, column=0)

        self.step2_instructions = tk.Label(self.category_frame, font=TEXT_FONT, bg=self.tab_color,
                              text="Enter a run group name and prefix.")
        self.step2_instructions.grid(row=1, column=1, padx=5, sticky="W", columnspan=2)

        self.name_lbl = tk.Label(self.category_frame, font=TEXT_FONT, bg=self.tab_color, text="Name:")
        self.name_lbl.grid(row=2, column=1, padx=5, sticky="W")

        self.category_name = EntryWithPlaceholder(self.category_frame, placeholder="ex: Primary Copper Manufacturing")
        self.category_name["width"] = 36
        self.category_name.grid(row=2, column=2, sticky="W")

        self.prefix_lbl = tk.Label(self.category_frame, font=TEXT_FONT, bg=self.tab_color, text="Prefix:")
        self.prefix_lbl.grid(row=3, column=1, padx=5, sticky="W")
        self.category_prefix = EntryWithPlaceholder(self.category_frame, placeholder="ex: PCM")
        self.category_prefix["width"] = 8
        self.category_prefix.grid(row=3, column=2, sticky="W")

        # Third step - configure report parameters
        self.step3 = tk.Label(self.parameters_frame, text="3.", font=TEXT_FONT, bg=self.tab_color, anchor="w")
        self.step3.grid(pady=10, padx=10, row=1, column=0)

        self.step3_instructions = tk.Label(self.parameters_frame, font=TEXT_FONT, bg=self.tab_color,
                                   text="Choose Radius and Risk Level (reports will be created for each combination.)")
        self.step3_instructions.grid(row=1, column=1, padx=5, sticky="W", columnspan=4)

        self.add_config(radius=50, cancer_risk=1, hi_risk=1)
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

    def reset(self):
        self.step1_instructions["text"] = "Select output folder"
        self.fullpath = None

        self.category_name.put_placeholder()
        self.category_prefix.put_placeholder()

        for frame in self.combinations.values():
            frame.grid_forget()

        self.combinations = {}

        self.add_config(radius=50, cancer_risk=1, hi_risk=1)

        if self.add_config_btn is None:
            self.create_add_config()

        self.nav.peopleLabel.configure(image=self.nav.ejIcon)
        self.titleLabel.configure(image=self.nav.ejIcon)

    def browse(self, icon, event):
        self.fullpath = tk.filedialog.askdirectory()
        icon["text"] = self.fullpath.split("/")[-1]

    # Note that when a config is removed, the add config button may have to reappear...
    def remove_config(self, config):

        if len(self.combinations) > 1:
            self.combinations[config].destroy()
            del self.combinations[config]

            if self.add_config_btn is None:
                self.create_add_config()

            # sort all remaining rows and re-grid them one at a time in order to preserve the
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

    # Add next config in response to user pressing add config button
    def add_next_config(self):
        self.add_config(radius=None, cancer_risk=None, hi_risk=None)

        num_configs = len(self.combinations)
        if num_configs == 4:
            self.add_config_btn.grid_forget()
            self.add_config_btn = None

    def add_config(self, radius, cancer_risk, hi_risk):
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
                               text="Radius (km):")
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
        cancer_radio = tk.Radiobutton(new_frame, text="Cancer Risk Level        (in a million):", width=26,
                                      bg=frame_color,font=SMALL_TEXT_FONT, variable=self.radios[frame_name],
                                      name="cancer_radio", command=partial(self.handle_radio, new_frame), value=0)
        cancer_radio.grid(row=starting_row+1, column=2, padx=5, pady=0, sticky="NE")

        if cancer_risk is not None:
            risk_num.set_value(cancer_risk)
        risk_num.grid(row=starting_row+1, column=3, pady=3, sticky="NW")

        hi_radio = tk.Radiobutton(new_frame, text="Noncancer Risk/Hazard Index Level:", width=26,
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

        remove_btn = tk.Button(new_frame, text="Remove", bg='lightgrey', relief='solid', borderwidth=1,
                              command=partial(self.remove_config, config), font=SMALL_TEXT_FONT)
        remove_btn.grid(row=starting_row+1, column=4, sticky='E', padx=10)

        self.next_config += 1

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

    def create_toshi_dropdown(self):
        toshis = self.toshis.values()

        # Label and drop down list
        toshi_lbl = tk.Label(self.toshi_frame, text="Select TOSHI:", font=TEXT_FONT, bg=self.tab_color, padx=10)
        toshi_lbl.grid(column=1, row=2, padx=5)
        self.toshi_1_value = tk.StringVar()
        self.toshi_1 = ttk.Combobox(self.toshi_frame, textvariable=self.toshi_1_value)
        self.toshi_1['values'] = toshis
        self.toshi_1.current(0)
        self.toshi_1.grid(column=2, row=2)

        # Label and drop down list
        toshi_lbl = tk.Label(self.toshi_frame, text="Select TOSHI:", font=TEXT_FONT, bg=self.tab_color, padx=10)
        toshi_lbl.grid(column=1, row=3, padx=5)
        self.toshi_2_value = tk.StringVar()
        self.toshi_2 = ttk.Combobox(self.toshi_frame, textvariable=self.toshi_2_value)
        self.toshi_2['values'] = toshis
        self.toshi_2.current(0)
        self.toshi_2.grid(column=2, row=3)

        # Label and drop down list
        toshi_lbl = tk.Label(self.toshi_frame, text="Select TOSHI:", font=TEXT_FONT, bg=self.tab_color, padx=10)
        toshi_lbl.grid(column=1, row=4, padx=5)
        self.toshi_3_value = tk.StringVar()
        self.toshi_3 = ttk.Combobox(self.toshi_frame, textvariable=self.toshi_3_value)
        self.toshi_3['values'] = toshis
        self.toshi_3.current(0)
        self.toshi_3.grid(column=2, row=4)

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
                cancer_risk_value = int(cancer_risk_value) if cancer_selected else 1
                hi_risk_value = int(hi_risk_value) if not cancer_selected else 1
            except ValueError:
                messagebox.showinfo('Error', "Please ensure all radius and risk values are numbers.")
                return False

            if radius_value <= 0 or radius_value > 50:
                messagebox.showinfo('Error', "Please ensure all radius values satisfy 0 < radius <= 50.")
                return False

            if cancer_selected and (cancer_risk_value not in [1, 5, 10, 20, 30, 40, 50, 100, 200, 300]):
                messagebox.showinfo('Error', "Please ensure all cancer risk values are one of the following: " +
                                    "[1, 5, 10, 20, 30, 40, 50, 100, 200, 300]")
                return False

            if not cancer_selected and (hi_risk_value not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
                messagebox.showinfo('Error', "Please ensure all HI risk values are one of the following: " +
                                    "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]")
                return False

            existing = len(self.run_configs)
            self.run_configs[existing] = {'radius': radius_value, 'cancer_risk': cancer_risk_value,
                                          'hi_risk': hi_risk_value}

            self.run_configs[existing]['toshis'] = []

            # TODO
            # infer which TOSHIs to use based on data...

        return True

    def run_reports(self, event):
        # Verify all options ok
        options_ok = self.verify_options()

        # Launch the runner
        if options_ok:

            existing = len(self.run_configs)
            Logger.logMessage("Ready to run " + str(existing) + " run combinations.")

            self.nav.peopleLabel.configure(image=self.nav.greenIcon)
            self.titleLabel.configure(image=self.nav.greenIcon)

            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(self.create_reports)

    def create_reports(self):

        # First, load the ACS datasets needed for analysis (if they haven't already been loaded...)
        Logger.logMessage("Loading ACS data...")
        try:
            if self.acs_df is None:
                acs = ACSDataset(path="resources/acs.xlsx")
                self.acs_df = acs.dataframe

            if self.levels_df is None:
                levels = ACSCountyTract(path="resources/acs-levels.xlsx")
                self.levels_df = levels.dataframe
        except FileNotFoundError:
            messagebox.showinfo("Missing files",
                            "Unable to find required ACS data. Please check your HEM4 resources folder and try again.")

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
        # TODO (dispose on every run? new sub folder?)
        output_dir = os.path.join(self.fullpath, "ej")
        if not (os.path.exists(output_dir) or os.path.isdir(output_dir)):
            Logger.logMessage("Creating ej directory for results...")
            os.mkdir(output_dir)

        # Finally, create reports for each requested combination of parameters
        config_num = 1
        for config in self.run_configs.values():
            Logger.logMessage("Creating EJ reports for combination #" + str(config_num))

            # Filter out MIR HI records that are outside the requested radius
            # Note the km to m conversion here!
            maxdist = config["radius"] * 1000

            filtered_mir_hi_df = self.all_receptors_df.query('distance <= @maxdist').copy()
            Logger.logMessage("Filtered MIR HI All Receptors dataset (radius = " + str(maxdist) + ") contains " +
                              str(len(filtered_mir_hi_df)) + " records.")

            # Infer which TOSHIs to include from the filtered all receptors file
            # should be of this form: {'Deve':'Developmental', 'Neur':'Neurological', ...}
            toshis = self.choose_toshis(filtered_mir_hi_df)

            ej = EnvironmentalJustice(mir_rec_df=filtered_mir_hi_df, acs_df=self.acs_df, levels_df=self.levels_df,
                                      outputdir=output_dir, source_cat_name=self.category_name.get_text_value(),
                                      source_cat_prefix=self.category_prefix.get_text_value(), radius=int(config["radius"]),
                                      cancer_risk_threshold=int(config["cancer_risk"]),
                                      hi_risk_threshold=int(config["hi_risk"]), requested_toshis=toshis)

            try:
                ej.create_reports()
            except BaseException as e:
                print(e)

            config_num += 1

        messagebox.showinfo("Environmental Justice Reports Finished", "Please check the output folder for reports.")
        self.reset()

    def choose_toshis(self, df):
        chosen = {}

        toshis = {hi_resp:'Resp', hi_live:'Live', hi_neur:'Neur', hi_deve:'Deve', hi_repr:'Repr', hi_kidn:'Kidn',
                  hi_ocul:'Ocul', hi_endo:'Endo', hi_hema:'Hemo', hi_immu:'Immu', hi_skel:'Skel', hi_sple:'Sple',
                  hi_thyr:'Thyr', hi_whol:'Whol'}

        for toshi in toshis:
            df_new = df[df[toshi] >= 1.5]
            if len(df_new) > 0:
                prefix = toshis[toshi]
                chosen[prefix] = self.toshis[prefix]

        Logger.logMessage("TOSHIs chosen: ")
        Logger.logMessage(', '.join(list(chosen.values())))

        return chosen