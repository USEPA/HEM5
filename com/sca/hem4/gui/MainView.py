import tkinter as tk
import PIL.Image
from PIL import ImageTk
from com.sca.hem4.gui.Styles import TAB_FONT
from functools import partial
import webbrowser

from com.sca.hem4.gui.Analyze import Analyze
from com.sca.hem4.gui.Census import Census
from com.sca.hem4.gui.Hem import Hem
from com.sca.hem4.gui.Log import Log
from com.sca.hem4.gui.Start import Start
from com.sca.hem4.gui.Summary import Summary


class MainView(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master=master, *args, **kwargs)

        #set mainframe background color
        self.main_color = "white"
        self.tab_color = "lightcyan3"
        self.highlightcolor = "snow3"
        self.current_button = []


        self.home = master
        self.container = tk.Frame(self, width=750, height=600, bg=self.main_color)
        self.container.pack(fill="both", expand=True)

        #instantiate start page
        self.nav = Start(self)
        self.nav.place(in_=self.container, relx=0.3, relwidth=0.7, relheight=1)

        #instantiate log tab
        self.log = Log(self)
        self.log.place(in_=self.container, relx=0.3, relwidth=0.7, relheight=1)
        self.log.lower()

        #instantiate hem4 start page
        self.hem = Hem(self)
        self.hem.place(in_=self.container, relx=0.3, relwidth=0.7, relheight=1)
        self.hem.lower()

        #instantiate summary tab
        self.summary = Summary(self)
        self.summary.place(in_=self.container, relx=0.3, relwidth=0.7, relheight=1)
        self.summary.lower()

        #instantiate analyze outputs
        self.analyze = Analyze(self)
        self.analyze.place(in_=self.container, relx=0.3, relwidth=0.7, relheight=1)
        self.analyze.lower()


        self.options = Census(self)
        self.options.place(in_=self.container, relx=0.3, relwidth=0.7, relheight=1)
        self.options.lower()

        #%%
        #HEM4 nav button
        self.newrunLabel= tk.Label(self, text="RUN HEM4", font=TAB_FONT, bg=self.main_color, height=2, pady=2, anchor="w")
        self.newrunLabel.place(in_=self.container, relwidth=0.2, relx=0.1, rely=0.09)

        #add run icon with margin for highlight
        #ri = PIL.Image.open('images\loading-png-gif-transparent.png').resize((30,30))
        self.ri = PIL.Image.open('images\icons8-virtual-machine-52.png').resize((30,30))
        self.gi = PIL.Image.open('images\icons8-green-circle-48.png').resize((30,30))
        self.cani = PIL.Image.open('images\icons8-cancel-48.png').resize((30,30))


        run_new = self.add_margin(self.ri, 5, 0, 5, 0)
        run_change = self.add_margin(self.gi, 5, 0, 5, 0)
        cancel_change = self.add_margin(self.cani, 5, 0, 5, 0)

        self.runIcon = ImageTk.PhotoImage(run_new)
        self.greenIcon = ImageTk.PhotoImage(run_change)
        self.cancelIcon = ImageTk.PhotoImage(cancel_change)


        self.iconLabel = tk.Label(self, image=self.runIcon, bg=self.main_color)
        self.iconLabel.image = self.runIcon # keep a reference!
        self.iconLabel.place(in_=self.container, relwidth=0.1, rely=0.09)

        #bind icon and label events
        self.newrunLabel.bind("<Enter>", partial(self.color_config, self.newrunLabel, self.iconLabel, self.highlightcolor))
        self.newrunLabel.bind("<Leave>", partial(self.color_config, self.newrunLabel, self.iconLabel, self.main_color))
        self.newrunLabel.bind("<Button-1>", partial(self.lift_page, self.newrunLabel, self.iconLabel, self.hem, self.current_button))

        self.iconLabel.bind("<Enter>", partial(self.color_config, self.iconLabel, self.newrunLabel, self.highlightcolor))
        self.iconLabel.bind("<Leave>", partial(self.color_config, self.iconLabel, self.newrunLabel,self.main_color))
        self.iconLabel.bind("<Button-1>", partial(self.lift_page, self.iconLabel, self.newrunLabel, self.hem, self.current_button))




        #%%

        #Options nav button
        self.optionsLabel= tk.Label(self, text="REVISE CENSUS DATA", font=TAB_FONT, bg=self.main_color, height=2, anchor="w")
        self.optionsLabel.place(in_=self.container, relwidth=0.2, rely=0.18, relx=0.1)

        #        #add run icon with margin for highlight
        oi = PIL.Image.open('images\icons8-settings-48.png').resize((30,30))
        oinew = self.add_margin(oi, 4, 0, 4, 0)

        optionIcon = ImageTk.PhotoImage(oinew)
        self.gearLabel = tk.Label(self, image=optionIcon, bg=self.main_color)
        self.gearLabel.image = optionIcon # keep a reference!
        self.gearLabel.place(in_=self.container, relwidth=0.1, rely=0.18)

        #bind icon and label events
        self.optionsLabel.bind("<Enter>", partial(self.color_config, self.optionsLabel, self.gearLabel, self.highlightcolor))
        self.optionsLabel.bind("<Leave>", partial(self.color_config, self.optionsLabel, self.gearLabel,self.main_color))
        self.optionsLabel.bind("<Button-1>", partial(self.lift_page, self.optionsLabel, self.gearLabel, self.options, self.current_button))

        self.gearLabel.bind("<Enter>", partial(self.color_config, self.gearLabel, self.optionsLabel, self.highlightcolor))
        self.gearLabel.bind("<Leave>", partial(self.color_config, self.gearLabel, self.optionsLabel,self.main_color))
        self.gearLabel.bind("<Button-1>", partial(self.lift_page, self.gearLabel, self.optionsLabel, self.options, self.current_button))

        # Risk Summary nav button
        self.riskLabel= tk.Label(self, text="SUMMARIZE RISKS", font=TAB_FONT, bg=self.main_color, height=2, pady=2, anchor="w")
        self.riskLabel.place(in_=self.container, relwidth=0.2, rely=0.27, relx=0.1)

        # add run icon with margin for highlight
        self.si = PIL.Image.open('images\icons8-edit-graph-report-48.png').resize((30,30))

        summary_new = self.add_margin(self.si, 5, 0, 5, 0)

        self.summaryIcon = ImageTk.PhotoImage(summary_new)

        self.summaryLabel = tk.Label(self, image=self.summaryIcon, bg=self.main_color)
        self.summaryLabel.image = self.summaryIcon # keep a reference!
        self.summaryLabel.place(in_=self.container, relwidth=0.1, rely=0.27)

        #bind icon and label events
        self.riskLabel.bind("<Enter>", partial(self.color_config, self.riskLabel, self.summaryLabel, self.highlightcolor))
        self.riskLabel.bind("<Leave>", partial(self.color_config, self.riskLabel, self.summaryLabel, self.main_color))
        self.riskLabel.bind("<Button-1>", partial(self.lift_page, self.riskLabel, self.summaryLabel, self.summary, self.current_button))

        self.summaryLabel.bind("<Enter>", partial(self.color_config, self.summaryLabel, self.riskLabel, self.highlightcolor))
        self.summaryLabel.bind("<Leave>", partial(self.color_config, self.summaryLabel, self.riskLabel, self.main_color))
        self.summaryLabel.bind("<Button-1>", partial(self.lift_page, self.summaryLabel, self.riskLabel, self.summary, self.current_button))

        #Analyze Outputs nav button
        self.analyzeLabel= tk.Label(self, text="ANALYZE OUTPUTS", font=TAB_FONT, bg=self.main_color, height=2, pady=2, anchor="w")
        self.analyzeLabel.place(in_=self.container, relwidth=0.2, rely=0.36, relx=0.1)

        #add run icon with margin for highlight
        ai = PIL.Image.open('images\icons8-graph-48.png').resize((30,30))
        analyzenew = self.add_margin(ai, 5, 0, 5, 0)

        analyzeIcon = ImageTk.PhotoImage(analyzenew)
        self.outputLabel = tk.Label(self, image=analyzeIcon, bg=self.main_color)
        self.outputLabel.image = analyzeIcon # keep a reference!
        self.outputLabel.place(in_=self.container, relwidth=0.1, rely=0.36)

        #bind icon and label events
        self.analyzeLabel.bind("<Enter>", partial(self.color_config, self.analyzeLabel, self.outputLabel, self.highlightcolor))
        self.analyzeLabel.bind("<Leave>", partial(self.color_config, self.analyzeLabel, self.outputLabel,self.main_color))
        self.analyzeLabel.bind("<Button-1>", partial(self.lift_page, self.analyzeLabel, self.outputLabel, self.analyze, self.current_button))

        self.outputLabel.bind("<Enter>", partial(self.color_config, self.outputLabel, self.analyzeLabel, self.highlightcolor))
        self.outputLabel.bind("<Leave>", partial(self.color_config, self.outputLabel, self.analyzeLabel,self.main_color))
        self.outputLabel.bind("<Button-1>", partial(self.lift_page, self.outputLabel, self.analyzeLabel, self.analyze, self.current_button))

        # Log nav button
        self.logLabel= tk.Label(self, text="LOG", font=TAB_FONT, bg=self.main_color, height=2, anchor="w")
        self.logLabel.place(in_=self.container, relwidth=0.2, rely=0.45, relx=0.1)

        # add run icon with margin for highlight
        self.li = PIL.Image.open('images\icons8-console-48.png').resize((30,30))
        linew = self.add_margin(self.li, 4, 0, 4, 0)

        logIcon = ImageTk.PhotoImage(linew)
        self.liLabel = tk.Label(self, image=logIcon, bg=self.main_color)
        self.liLabel.image = logIcon # keep a reference!
        self.liLabel.place(in_=self.container, relwidth=0.1, rely=0.45)

        #bind icon and label events
        self.logLabel.bind("<Enter>", partial(self.color_config, self.logLabel, self.liLabel, self.highlightcolor))
        self.logLabel.bind("<Leave>", partial(self.color_config, self.logLabel, self.liLabel, self.main_color))
        self.logLabel.bind("<Button-1>", partial(self.lift_page, self.logLabel, self.liLabel, self.log, self.current_button))

        self.liLabel.bind("<Enter>", partial(self.color_config, self.liLabel, self.logLabel, self.highlightcolor))
        self.liLabel.bind("<Leave>", partial(self.color_config, self.liLabel, self.logLabel,self.main_color))
        self.liLabel.bind("<Button-1>", partial(self.lift_page, self.liLabel, self.logLabel, self.log, self.current_button))

        # USER GUIDE

        # user nav button
        ugLabel= tk.Label(self, text="HEM4 USER GUIDE", font=TAB_FONT, bg=self.main_color, height=2, anchor="w")
        ugLabel.place(in_=self.container, relwidth=0.2, rely=0.72, relx=0.1)

        # add run icon with margin for highlight
        ug = PIL.Image.open('images\icons8-user-manual-48.png').resize((30,30))
        ugnew = self.add_margin(ug, 4, 0, 4, 0)

        ugIcon = ImageTk.PhotoImage(ugnew)
        bookLabel = tk.Label(self, image=ugIcon, bg=self.main_color)
        bookLabel.image = ugIcon # keep a reference!
        bookLabel.place(in_=self.container, relwidth=0.1, rely=0.72)

        # bind icon and label events
        ugLabel.bind("<Enter>", partial(self.color_config, ugLabel, bookLabel, self.highlightcolor))
        ugLabel.bind("<Leave>", partial(self.color_config, ugLabel, bookLabel, self.main_color))
        ugLabel.bind("<Button-1>", self.hyperlink1)
        bookLabel.bind("<Enter>", partial(self.color_config, bookLabel, ugLabel, self.highlightcolor))
        bookLabel.bind("<Leave>", partial(self.color_config, bookLabel, ugLabel,self.main_color))
        bookLabel.bind("<Button-1>", self.hyperlink1)

        #aermod user nav button
        agLabel= tk.Label(self, text="AERMOD USER GUIDE", font=TAB_FONT, bg=self.main_color, height=2, anchor="w")
        agLabel.place(in_=self.container, relwidth=0.2, rely=0.81, relx=0.1)

        #        #add run icon with margin for highlight
        ag = PIL.Image.open('images\icons8-user-manual-48.png').resize((30,30))
        agnew = self.add_margin(ag, 4, 0, 4, 0)

        agIcon = ImageTk.PhotoImage(agnew)
        bookLabel2 = tk.Label(self, image=agIcon, bg=self.main_color)
        bookLabel2.image = agIcon # keep a reference!
        bookLabel2.place(in_=self.container, relwidth=0.1, rely=0.81)

        #bind icon and label events
        agLabel.bind("<Enter>", partial(self.color_config, agLabel, bookLabel2, self.highlightcolor))
        agLabel.bind("<Leave>", partial(self.color_config, agLabel, bookLabel2, self.main_color))
        agLabel.bind("<Button-1>", self.hyperlink2)
        bookLabel2.bind("<Enter>", partial(self.color_config, bookLabel2, agLabel, self.highlightcolor))
        bookLabel2.bind("<Leave>", partial(self.color_config, bookLabel2, agLabel,self.main_color))
        bookLabel2.bind("<Button-1>", self.hyperlink2)

        #aermod user nav button
        closeLabel= tk.Label(self, text="EXIT", font=TAB_FONT, bg=self.main_color, height=2, anchor="w")
        closeLabel.place(in_=self.container, relwidth=0.2, rely=0.90, relx=0.1)

        # add run icon with margin for highlight
        clo = PIL.Image.open('images\icons8-close-window-48.png').resize((30,30))
        clonew = self.add_margin(clo, 4, 0, 4, 0)

        closeIcon = ImageTk.PhotoImage(clonew)
        closeLabel2 = tk.Label(self, image=closeIcon, bg=self.main_color)
        closeLabel2.image = closeIcon # keep a reference!
        closeLabel2.place(in_=self.container, relwidth=0.1, rely=0.90)

        #bind icon and label events
        closeLabel.bind("<Enter>", partial(self.color_config, closeLabel, closeLabel2, self.highlightcolor))
        closeLabel.bind("<Leave>", partial(self.color_config, closeLabel, closeLabel2, self.main_color))
        closeLabel.bind("<Button-1>", partial(self.on_closing, self.hem))
        closeLabel2.bind("<Enter>", partial(self.color_config, closeLabel2, closeLabel, self.highlightcolor))
        closeLabel2.bind("<Leave>", partial(self.color_config, closeLabel2, closeLabel,self.main_color))
        closeLabel2.bind("<Button-1>", partial(self.on_closing, self.hem))

    # setting geometry of tk window
    def lift_page(self, widget1, widget2, page, previous, event):
        """
        Function lifts page and changes button color to active,
        changes previous button color
        """
        try:
            widget1.configure(bg=self.tab_color)
            widget2.configure(bg=self.tab_color)

            if len(self.current_button) > 0:

                for i in self.current_button:
                    i.configure(bg=self.main_color)

            print('Current Button before:', self.current_button)
            print('page:', page)
            page.lift()
            self.current_button = [widget1, widget2]
            print('Current Button after:', self.current_button)
        except Exception as e:

            print(e)


    def color_config(self, widget1, widget2, color, event):

        if widget1 not in self.current_button and widget2 not in self.current_button:
            widget1.configure(bg=color)
            widget2.configure(bg=color)

    def add_margin(self, pil_img, top, right, bottom, left):
        width, height = pil_img.size
        new_width = width + right + left
        new_height = height + top + bottom
        result = PIL.Image.new(pil_img.mode, (new_width, new_height))
        result.paste(pil_img, (left, top))
        return result

    def hyperlink1(self, event):
        webbrowser.open_new(r"https://www.epa.gov/fera/risk-assessment-and-"+
                            "modeling-human-exposure-model-hem")

    def hyperlink2(self, event):
        webbrowser.open_new(r"https://www3.epa.gov/ttn/scram/models/aermod/aermod_userguide.pdf")

    def on_closing(self, hem, event):

        if hem.running == True:

            hem.quit_app()
            if hem.aborted == True:
                self.home.destroy()

        else:
            self.home.destroy()
