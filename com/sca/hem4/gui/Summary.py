from datetime import datetime

from com.sca.hem4.gui.Page import Page
import tkinter as tk
import tkinter.ttk as ttk
import PIL.Image
from PIL import ImageTk
from com.sca.hem4.gui.Styles import TITLE_FONT, TEXT_FONT, MAIN_COLOR
from functools import partial
from tkinter.filedialog import askopenfilename
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox

from com.sca.hem4.log import Logger
from com.sca.hem4.summary.SummaryManager import SummaryManager
from com.sca.hem4.writer.excel.FacilityMaxRiskandHI import FacilityMaxRiskandHI
import os
import glob


class Summary(Page):

    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.nav = nav

        self.checked = []
        self.checked_icons = []

        meta_container = tk.Frame(self, bg=self.tab_color, bd=2)
        meta_container.pack(side="top", fill="both", expand=True)

        self.filler = tk.Frame(self, bg=self.tab_color, height=200)
        self.filler.pack(side="left", fill="both", expand=True)

        self.meta_two = tk.Frame(self, bg=self.tab_color, height=200)
        self.meta_two.pack(side="right", fill="both")
        self.meta_two.columnconfigure(3, weight=1)

        self.container = tk.Frame(meta_container, bg=self.tab_color, borderwidth=0)
        self.container.grid(row=0, column=0)
        self.container.grid_rowconfigure(11, weight=1)

        # create grid
        self.s1 = tk.Frame(self.container, width=600, height=50, bg=self.tab_color)
        self.s2 = tk.Frame(self.container, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s4 = tk.Frame(self.container, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.l4 = tk.Frame(self.s4, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.r4 = tk.Frame(self.s4, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s5 = tk.Frame(self.container, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.l5 = tk.Frame(self.s5, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.r5 = tk.Frame(self.s5, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s6 = tk.Frame(self.container, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.l6 = tk.Frame(self.s6, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.r6 = tk.Frame(self.s6, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s7 = tk.Frame(self.container, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.l7 = tk.Frame(self.s7, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.r7 = tk.Frame(self.s7, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s8 = tk.Frame(self.container, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.l8 = tk.Frame(self.s8, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.r8 = tk.Frame(self.s8, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s9 = tk.Frame(self.container, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.r9 = tk.Frame(self.s9, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.l9 = tk.Frame(self.s9, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.s10 = tk.Frame(self.container, width=600, height=50, pady=5, padx=5, bg=self.tab_color)
        self.l10 = tk.Frame(self.s10, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        self.r10 = tk.Frame(self.s10, width=300, height=50, pady=5, padx=5, bg=self.tab_color)
        # self.s11 = tk.Frame(self.container, width=600, height=50, pady=5, padx=5, bg=self.tab_color)

        self.container.grid_rowconfigure(12, weight=1)
        self.container.grid_columnconfigure(2, weight=1)
        self.container.grid(sticky="nsew")
        self.s1.grid(row=1, column=0, columnspan=4, sticky="nsew")
        self.s2.grid(row=2, column=0, columnspan=4, sticky="nsew")
        self.s4.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.l4.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.r4.grid(row=1, column=2, columnspan=2, sticky="nsew")
        self.s5.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.l5.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.r5.grid(row=1, column=2, columnspan=2, sticky="nsew")
        self.s6.grid(row=5, column=0, columnspan=2, sticky="nsew")
        self.l6.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.r6.grid(row=1, column=2, columnspan=2, sticky="nsew")
        self.s7.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.l7.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.r7.grid(row=1, column=2, columnspan=2, sticky="nsew")
        self.s8.grid(row=7, column=0, columnspan=2, sticky="nsew")
        self.l8.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.r8.grid(row=1, column=2, columnspan=2, sticky="nsew")
        self.s9.grid(row=8, column=0, columnspan=2, sticky="nsew")
        self.l9.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.r9.grid(row=1, column=2, columnspan=2, sticky="nsew")
        self.s10.grid(row=9, column=0, columnspan=2, sticky="nsew")
        self.l10.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.r10.grid(row=1, column=2, columnspan=2, sticky="nsew")
        # self.s11.grid(row=10, column=0, columnspan=2, sticky="nsew")

        self.tt = PIL.Image.open('images\icons8-edit-graph-report-48-white.png').resize((30,30))
        self.tticon = self.add_margin(self.tt, 5, 0, 5, 0)
        self.titleicon = ImageTk.PhotoImage(self.tticon)
        self.titleLabel = tk.Label(self.s1, image=self.titleicon, bg=self.tab_color)
        self.titleLabel.image = self.titleicon # keep a reference!
        self.titleLabel.grid(row=1, column=0, padx=10, pady=10)

        #title
        title = tk.Label(self.s1, text="CREATE RISK SUMMARY REPORTS", font=TITLE_FONT, fg=MAIN_COLOR, bg=self.tab_color, anchor="w")
        title.grid(row=1, column=1, pady=10, padx=10)

        fu = PIL.Image.open('images\icons8-folder-48.png').resize((30,30))
        ficon = self.add_margin(fu, 5, 0, 5, 0)
        fileicon = ImageTk.PhotoImage(ficon)
        self.fileLabel = tk.Label(self.s2, image=fileicon, bg=self.tab_color)
        self.fileLabel.image = fileicon # keep a reference!
        self.fileLabel.grid(row=1, column=0, padx=10)

        self.folder_select = tk.Label(self.s2,
                                      text="Select output folder", font=TITLE_FONT, bg=self.tab_color, anchor="w")
        self.folder_select.grid(pady=10, padx=10, row=1, column=1)
        self.fileLabel.bind("<Button-1>", partial(self.browse, self.folder_select))
        self.folder_select.bind("<Button-1>", partial(self.browse, self.folder_select))

        # unchecked box icon
        ui = PIL.Image.open('images\icons8-unchecked-checkbox-48.png').resize((30,30))
        unchecked = self.add_margin(ui, 5, 0, 5, 0)
        self.uncheckedIcon = ImageTk.PhotoImage(unchecked)

        # checked box icon
        ci = PIL.Image.open('images\icons8-checked-checkbox-48.png').resize((30,30))
        checked = self.add_margin(ci, 5, 0, 5, 0)
        self.checkedIcon = ImageTk.PhotoImage(checked)

        self.add_report_checkbox("Max Risk", self.l4, self.check_box)
        self.add_report_checkbox("Cancer Drivers", self.l5, self.check_box)
        self.add_report_checkbox("Hazard Index Drivers", self.l6, self.check_box)
        self.add_report_checkbox("Risk Histogram", self.l7, self.check_box)
        self.add_report_checkbox("Hazard Index Histogram", self.l8, self.check_box)
        self.add_report_checkbox("Incidence Drivers", self.l9, self.check_box)
        self.add_report_checkbox("Acute Impacts", self.l10, self.check_box)
        self.add_report_checkbox("Multipathway", self.r4, self.check_box)
        self.add_report_checkbox("Max Concentration", self.r5, self.set_hap)
        self.add_report_checkbox("Max Risk and HI by Source\nand Pollutant", self.r6, self.set_max_risk_sourcetype)
        self.add_report_checkbox("Source Type Risk Histogram", self.r7, self.set_sourcetype)

        ru = PIL.Image.open('images\icons8-create-48.png').resize((30,30))
        ricon = self.add_margin(ru, 5, 0, 5, 0)
        rileicon = ImageTk.PhotoImage(ricon)
        rileLabel = tk.Label(self.meta_two, image=rileicon, bg=self.tab_color)
        rileLabel.image = rileicon # keep a reference!
        rileLabel.grid(row=1, column=1, padx=0, pady=20, sticky='E')

        run_button = tk.Label(self.meta_two, text="Run Reports", font=TEXT_FONT, bg=self.tab_color)
        run_button.grid(row=1, column=2, padx=20, pady=20, sticky='W')

        run_button.bind("<Enter>", partial(self.color_config, run_button, rileLabel, self.meta_two, 'light grey'))
        run_button.bind("<Leave>", partial(self.color_config, run_button, rileLabel, self.meta_two, self.tab_color))
        run_button.bind("<Button-1>", self.run_reports)

        rileLabel.bind("<Enter>", partial(self.color_config, rileLabel, run_button, self.meta_two, 'light grey'))
        rileLabel.bind("<Leave>", partial(self.color_config, rileLabel, run_button, self.meta_two, self.tab_color))
        rileLabel.bind("<Button-1>", self.run_reports)

    def add_report_checkbox(self, name, container, callback):
        # Create a new frame to hold both inputs
        frame = tk.Frame(container, width=300, height=50, pady=0, padx=0, bg=self.tab_color)
        frame.grid(row=1, column=1, columnspan=4, padx=0, sticky="W")

        label = tk.Label(frame, font=TEXT_FONT, width=22, anchor='w', bg=self.tab_color, text=name)
        label.grid(row=1, column=4, padx=5, sticky="w")

        # unchecked box
        self.report_label = tk.Label(frame, image=self.uncheckedIcon, bg=self.tab_color)
        self.report_label.image = self.uncheckedIcon
        self.report_label.grid(row=1, column=3, padx=10, sticky='w')
        self.report_label.bind("<Button-1>", partial(callback, self.report_label, name))
        label.bind("<Button-1>", partial(callback, self.report_label, name))
        container.bind("<Button-1>", partial(callback, self.report_label, name))

    # Generic callback that simply manages the checkbox
    def check_box(self, icon, text, event):

        if text not in self.checked:
            icon.configure(image=self.checkedIcon)
            self.checked.append(text)
            self.checked_icons.append(icon)

        elif text in self.checked:
            icon.configure(image=self.uncheckedIcon)
            self.checked.remove(text)
            self.checked_icons.remove(icon)

    # Source type histogram callback that presents two inputs for required parameters
    def set_sourcetype(self, icon, text, event):

        if text not in self.checked:
            icon.configure(image=self.checkedIcon)
            self.checked.append(text)
            self.checked_icons.append(icon)
            self.pos = tk.Label(self.r8, font=TEXT_FONT, bg=self.tab_color, text="Enter the position in the source ID where the\n source type begins.The default is 1.")
            self.pos.grid(row=1, column=4, padx=5, sticky="W")
            self.pos_num = ttk.Entry(self.r8)
            self.pos_num["width"] = 5
            self.pos_num.grid(row=1, column=3, padx=5, sticky="W")
            self.chars = tk.Label(self.r9, font=TEXT_FONT, bg=self.tab_color, text="Enter the number of characters \nin the sourcetype ID.")
            self.chars.grid(row=1, column=4, padx=5, sticky="W")
            self.chars_num = ttk.Entry(self.r9)
            self.chars_num["width"] = 5
            self.chars_num.grid(row=1, column=3, padx=5, sticky="W")

        elif text in self.checked:

            icon.configure(image=self.uncheckedIcon)
            self.checked.remove(text)
            self.checked_icons.remove(icon)
            self.pos.destroy()
            self.pos_num.destroy()
            self.chars.destroy()
            self.chars_num.destroy()

    # Source type histogram callback that presents two inputs for required parameters
    def set_max_risk_sourcetype(self, icon, text, event):

        if text not in self.checked:

            icon.configure(image=self.checkedIcon)
            self.checked.append(text)
            self.checked_icons.append(icon)
            self.max_risk_pos = tk.Label(self.r6, font=TEXT_FONT, bg=self.tab_color,
                                         text="Enter the position in the source ID where the\n source type begins.The default is 1.")
            self.max_risk_pos.grid(row=2, column=4, padx=5, sticky="W")
            self.max_risk_pos_num = ttk.Entry(self.r6)
            self.max_risk_pos_num["width"] = 5
            self.max_risk_pos_num.grid(row=2, column=3, padx=5, sticky="W")
            self.max_risk_chars = tk.Label(self.r6, font=TEXT_FONT, bg=self.tab_color,
                                           text="Enter the number of characters \nin the sourcetype ID.")
            self.max_risk_chars.grid(row=3, column=4, padx=5, sticky="W")
            self.max_risk_chars_num = ttk.Entry(self.r6)
            self.max_risk_chars_num["width"] = 5
            self.max_risk_chars_num.grid(row=3, column=3, padx=5, sticky="W")

        elif text in self.checked:

            icon.configure(image=self.uncheckedIcon)
            self.checked.remove(text)
            self.checked_icons.remove(icon)
            self.max_risk_pos.destroy()
            self.max_risk_pos_num.destroy()
            self.max_risk_chars.destroy()
            self.max_risk_chars_num.destroy()

    # Max conc callback that presents pollutant name parameter
    def set_hap(self, icon, text, event):

        if text not in self.checked:
            icon.configure(image=self.checkedIcon)
            self.checked.append(text)
            self.checked_icons.append(icon)

            # Create a new frame to hold both the input and the instructions
            self.n5 = tk.Frame(self.r5, width=300, height=50, pady=0, padx=0, bg=self.tab_color)
            self.n5.grid(row=2, column=1, columnspan=4, padx=0, sticky="w")
            self.pollutant_label = tk.Label(self.n5, font=TEXT_FONT, bg=self.tab_color, text="Enter a pollutant name")
            self.pollutant_label.grid(row=1, column=4, padx=5, sticky="w")
            self.pollutant_name = ttk.Entry(self.n5)
            self.pollutant_name["width"] = 20
            self.pollutant_name.grid(row=1, column=3, padx=5, sticky="w")

        elif text in self.checked:
            icon.configure(image=self.uncheckedIcon)
            self.checked.remove(text)
            self.checked_icons.remove(icon)
            self.pollutant_label.destroy()
            self.pollutant_name.destroy()
            self.n5.destroy()

    def add_margin(self, pil_img, top, right, bottom, left):
        width, height = pil_img.size
        new_width = width + right + left
        new_height = height + top + bottom
        result = PIL.Image.new(pil_img.mode, (new_width, new_height))
        result.paste(pil_img, (left, top))
        return result

    def browse(self, icon, event):


        self.fullpath = tk.filedialog.askdirectory()
        print(self.fullpath)
        icon["text"] = self.fullpath.split("/")[-1]

    def run_reports(self, event):

        self.nav.summaryLabel.configure(image=self.nav.greenIcon)

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.createReports)

        if self.reports_ready:
            self.lift_page(self.nav.liLabel, self.nav.logLabel, self.nav.log, self.nav.current_button)

    def createReports(self,  arguments=None):

        self.reports_ready = False

        # set log file to append to in folder
        logpath = self.fullpath +"/hem4.log"

        # open log
        self.logfile = open(logpath, 'a')
        now = str(datetime.now())

        # Figure out which facilities will be included in the report.
        # Facilities listed in the facility_max_risk_and_hi HEM4 output will be used
        # and the modeling group name is taken from the first part of the filename.
        try:
            skeleton = os.path.join(self.fullpath, '*facility_max_risk_and_hi.xl*')
            print(skeleton)
            fname = glob.glob(skeleton)
            print(fname)

            if fname:
                head, tail = os.path.split(fname[0])
                groupname = tail[:tail.find('facility_max_risk_and_hi')-1]
                facmaxrisk = FacilityMaxRiskandHI(targetDir=self.fullpath, filenameOverride=tail)
                facmaxrisk_df = facmaxrisk.createDataframe()
                faclist = facmaxrisk_df['Facil_id'].tolist()
            else:
                Logger.logMessage("Cannot generate summaries because there is no Facility_Max_Risk_and_HI Excel file \
                                  in the folder you selected.")
                messagebox.showinfo("Error", "Cannot generate summaries because there is no Facility_Max_Risk_and_HI \
                                    Excel file in the folder you selected.")

        except Exception as e:
            print(e)
            print("No facilities selected.",
                  "Please select a run folder.")
            messagebox.showinfo("No facilities selected",
                                "Please select a run folder.")

        # get reports and set arguments
        reportNames = []
        reportNameArgs = {}
        try:
            for report in self.checked:
                print(self.checked)

                if report == 'Max Risk':
                    reportNames.append('MaxRisk')
                    reportNameArgs['MaxRisk'] = None
                if report == 'Cancer Drivers':
                    reportNames.append('CancerDrivers')
                    reportNameArgs['CancerDrivers'] = None
                if report == 'Hazard Index Drivers':
                    reportNames.append('HazardIndexDrivers')
                    reportNameArgs['HazardIndexDrivers'] = None
                if report == 'Risk Histogram':
                    reportNames.append('Histogram')
                    reportNameArgs['Histogram'] = None
                if report == 'Hazard Index Histogram':
                    reportNames.append('HI_Histogram')
                    reportNameArgs['HI_Histogram'] = None
                if report == 'Incidence Drivers':
                    reportNames.append('IncidenceDrivers')
                    reportNameArgs['IncidenceDrivers'] = None
                if report == "Acute Impacts":
                    reportNames.append('AcuteImpacts')
                    reportNameArgs['AcuteImpacts'] = None
                if report == "Max Concentration":
                    reportNames.append('MaxConcentrationLocator')
                    reportNameArgs['MaxConcentrationLocator'] = self.pollutant_name.get()
                if report == "Max Risk and HI by Source\nand Pollutant":
                    reportNames.append('SourcePollutantMaxRisk')
                    # Pass starting position and number of characters
                    # Translate user supplied starting position to array index value (0-based indexing)
                    if self.max_risk_pos_num.get() == '' or self.max_risk_pos_num.get() == '0':
                        startpos = 0
                        print(startpos)
                    else:
                        startpos = int(self.max_risk_pos_num.get()) - 1
                        print(startpos)

                    # Convert non-numeric to 0 (handles blank case)
                    if self.max_risk_chars_num.get().isnumeric():
                        numchars = int(self.max_risk_chars_num.get())
                    else:
                        numchars = 0
                    print(numchars)

                    reportNameArgs['SourcePollutantMaxRisk'] = [startpos, numchars]

                if report == "Source Type Risk Histogram":
                    reportNames.append('SourceTypeRiskHistogram')
                    # Pass starting position and number of characters
                    # Translate user supplied starting position to array index value (0-based indexing)
                    if self.pos_num.get() == '' or self.pos_num.get() == '0':
                        startpos = 0
                        print(startpos)
                    else:
                        startpos = int(self.pos_num.get()) - 1
                        print(startpos)

                    # Convert non-numeric to 0 (handles blank case)
                    if self.chars_num.get().isnumeric():
                        numchars = int(self.chars_num.get())
                    else:
                        numchars = 0
                    print(numchars)

                    reportNameArgs['SourceTypeRiskHistogram'] = [startpos, numchars]

                if report == "Multipathway":
                    reportNames.append('MultiPathway')
                    reportNameArgs['MultiPathway'] = None

        except Exception as e:
            print(e)

        # add run checks
        if len(self.checked) == 0:
            messagebox.showinfo("No report selected", "Please select one or more report types to run.")
        else:

            self.reports_ready = True

            # extra conditions for reports with parameters
            if "Source Type Risk Histogram" in self.checked or \
                    "Max Risk and HI by Source\nand Pollutant" in self.checked:
                if startpos < 0:
                    messagebox.showinfo('Invalid starting position',
                                        'Starting position of the sourcetype ID must be > 0.')
                    self.reports_ready = False
                elif numchars <= 0:
                    messagebox.showinfo('Invalid number of sourcetype ID characters',
                                        'Please enter a valid number of characters of the sourcetype ID.')
                    self.reports_ready = False

            if "Max Concentration" in self.checked:
                if self.pollutant_name.get() == "":
                    messagebox.showinfo('Invalid pollutant',
                                        'Pollutant must not be blank.')
                    self.reports_ready = False

        # if checks have been passed
        if self.reports_ready:
            running_message = "\nRunning report(s) on facilities: " + ', '.join(faclist)

            # write to log
            self.logfile.write(str(datetime.now()) + ":    " + running_message + "\n")
            self.nav.log.scr.configure(state='normal')
            self.nav.log.scr.insert(tk.INSERT, running_message)
            self.nav.log.scr.insert(tk.INSERT, "\n")
            self.nav.log.scr.configure(state='disabled')

            self.titleLabel.configure(image=self.nav.greenIcon)
            summaryMgr = SummaryManager(self.fullpath, groupname, faclist)

            # loop through for each report selected
            for reportName in reportNames:
                report_message = "Creating " + reportName + " report."

                self.nav.log.scr.configure(state='normal')
                self.nav.log.scr.insert(tk.INSERT, report_message)
                self.nav.log.scr.insert(tk.INSERT, "\n")
                self.nav.log.scr.configure(state='disabled')

                self.logfile.write(str(datetime.now()) + ":    " + report_message + "\n")

                args = reportNameArgs[reportName]
                summaryMgr.createReport(self.fullpath, reportName, args)

                if summaryMgr.status:
                    report_complete = reportName +  " complete."
                    self.nav.log.scr.configure(state='normal')
                    self.nav.log.scr.insert(tk.INSERT, report_complete)
                    self.nav.log.scr.insert(tk.INSERT, "\n")
                    self.nav.log.scr.configure(state='disabled')
                    self.logfile.write(str(datetime.now()) + ":    " + report_complete + "\n")
                else:
                    break

            self.nav.log.scr.configure(state='normal')
            self.nav.log.scr.insert(tk.INSERT, "Risk Summary Reports Finished.")
            self.nav.log.scr.insert(tk.INSERT, "\n")
            self.nav.log.scr.configure(state='disabled')
            self.logfile.write(str(datetime.now()) + ":    " + "Risk Summary Reports Finished." + "\n")

            self.titleLabel.configure(image=self.titleicon)

            messagebox.showinfo("Summary Reports Finished", "Risk summary reports for  " + ', '.join(faclist) + " run.")

            if "Source Type Risk Histogram" in self.checked:
                self.pos.destroy()
                self.pos_num.destroy()
                self.chars.destroy()
                self.chars_num.destroy()

            if "Max Risk and HI by Source\nand Pollutant" in self.checked:
                self.max_risk_pos.destroy()
                self.max_risk_pos_num.destroy()
                self.max_risk_chars.destroy()
                self.max_risk_chars_num.destroy()

            if "Max Concentration" in self.checked:
                self.pollutant_name.destroy()
                self.pollutant_label.destroy()
                self.n5.destroy()

            for icon in self.checked_icons:
                icon.configure(image=self.uncheckedIcon)

            self.folder_select['text'] = "Select output folder"
            self.nav.summaryLabel.configure(image=self.nav.summaryIcon)
            self.logfile.close()

    def lift_page(self, widget1, widget2, page, previous):
        """
        Function lifts page and changes button color to active,
        changes previous button color
        """
        try:
            widget1.configure(bg=self.tab_color)
            widget2.configure(bg=self.tab_color)

            if len(self.nav.current_button) > 0:

                for i in self.nav.current_button:
                    i.configure(bg=self.main_color)

#            print('Current Button before:', self.nav.current_button)
#            print('page:', page)
            page.lift()
            self.nav.current_button = [widget1, widget2]
#            print('Current Button after:', self.nav.current_button)
        except Exception as e:
            print(e)

    def color_config(self, widget1, widget2, container, color, event):
        widget1.configure(bg=color)
        widget2.configure(bg=color)
        container.configure(bg=color)
