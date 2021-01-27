from tkinter import messagebox

from com.sca.hem4.gui.EntryWithPlaceholder import EntryWithPlaceholder
from com.sca.hem4.gui.Page import Page
import tkinter as tk
import tkinter.ttk as ttk
from com.sca.hem4.gui.Styles import TEXT_FONT, SMALL_TEXT_FONT, TITLE_FONT, MAIN_COLOR
import PIL.Image
from PIL import ImageTk
from functools import partial

class EJ(Page):
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.nav = nav
        self.configs = {}
        self.next_config = 1

        self.container = tk.Frame(self, bg=self.tab_color, bd=2)
        self.container.pack(side="top", fill="both", expand=True)

        self.run_container = tk.Frame(self, bg='blue', height=200)
        self.run_container.pack(side="bottom", fill="both")

        # create grid
        self.title_frame = tk.Frame(self.container, height=100, bg=self.tab_color)
        self.folder_frame = tk.Frame(self.container, height=150, pady=5, padx=5, bg=self.tab_color)
        self.category_frame = tk.Frame(self.container, height=200, pady=5, padx=5, bg=self.tab_color)
        self.parameters_frame = tk.Frame(self.container, height=200, pady=5, padx=5, bg=self.tab_color)

        self.title_frame.grid(row=1, columnspan=5, sticky="nsew")
        self.folder_frame.grid(row=2, columnspan=5, sticky="nsew")
        self.category_frame.grid(row=3, columnspan=5, sticky="nsew")
        self.parameters_frame.grid(row=4, columnspan=5, sticky="nsew")

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
                              text="Enter a source category name and prefix.")
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
        self.step3 = tk.Label(self.parameters_frame,
                              text="3.", font=TEXT_FONT, bg=self.tab_color, anchor="w")
        self.step3.grid(pady=10, padx=10, row=1, column=0)

        self.step3_instructions = tk.Label(self.parameters_frame, font=TEXT_FONT, bg=self.tab_color,
                                           text="Configure parameters (reports will be created for each configuration.)")
        self.step3_instructions.grid(row=1, column=1, padx=5, sticky="W", columnspan=4)

        self.add_config(radius=50, risk=1)
        self.create_add_config()


    # Event handlers for porting instructions
    def add_instructions(self, placeholder1, placeholder2):

        # Dynamic instructions place holder
        global instruction_instance
        self.instruction_instance = tk.StringVar(placeholder1)
        self.instruction_instance.set(" ")
        self.dynamic_inst = tk.Label(placeholder2, wraplength=600, font=TEXT_FONT, padx=20, bg=self.tab_color)
        self.dynamic_inst.config(height=4)

        self.dynamic_inst["textvariable"] = self.instruction_instance
        self.dynamic_inst.grid(row=0, column=0)

    def reset_instructions(self):
        """
        Function clears instructions from display box
        """
        global instruction_instance
        self.instruction_instance.set(" ")

    def browse(self, icon, event):
        self.fullpath = tk.filedialog.askdirectory()
        print(self.fullpath)
        icon["text"] = self.fullpath.split("/")[-1]

    def remove_config(self, config):

        if len(self.configs) > 1:
            self.configs[config].destroy()
            del self.configs[config]

            if self.add_config_btn is None:
                self.create_add_config()

            # sort all remaining rows and re-add them one at a time
            sorted_x = {k: self.configs[k] for k in sorted(self.configs)}
            new_frame_row = 1
            for config in sorted_x:
                self.configs[config].grid(row=new_frame_row+4, columnspan=5, padx=50, sticky="nsew")
                new_frame_row += 1
        else:
            messagebox.showinfo('Error', "You must have at least one configuration.")

    def create_add_config(self):
        self.add_config_btn = tk.Button(self.parameters_frame, text="Add config", bg='lightgrey', relief='solid',
                                        borderwidth=1, command=self.add_next_config, font=SMALL_TEXT_FONT)
        self.add_config_btn.grid(row=12, column=1, sticky='W', padx=7, pady=5)

    def add_next_config(self):
        self.add_config(radius=None, risk=None)

        num_configs = len(self.configs)
        if num_configs == 4:
            self.add_config_btn.grid_forget()
            self.add_config_btn = None

    def add_config(self, radius, risk):
        num_configs = len(self.configs)
        print("num configs before adding: " + str(num_configs))

        print("adding next config: " + str(self.next_config))
        config = self.next_config
        frame_color = 'lightyellow'
        new_frame = tk.Frame(self.parameters_frame, height=200, pady=5, padx=5, bg=frame_color,
                             highlightbackground="grey", highlightthickness=1)

        frame_row = (num_configs%4)+5
        print("new frame row: " + str(frame_row))
        new_frame.grid(row=frame_row, columnspan=5, padx=50, sticky="nsew")
        self.configs[config] = new_frame

        starting_row = 2
        config_lbl = tk.Label(new_frame, font=SMALL_TEXT_FONT, bg=frame_color,
                                   text="Configuration:")
        config_lbl.grid(row=starting_row, column=1, rowspan=2, columnspan=2, padx=10, sticky="W")

        step3a = tk.Label(new_frame, font=SMALL_TEXT_FONT, bg=frame_color,
                               text="Radius (km):")
        step3a.grid(row=starting_row, column=3, padx=5, pady=2, sticky="SE")
        radius_num = EntryWithPlaceholder(new_frame, placeholder="Enter a radius value <=50")
        radius_num["width"] = 30

        if radius is not None:
            radius_num.set_value(radius)
        radius_num.grid(row=starting_row, column=4, pady=3, sticky="SW")

        step3c = tk.Label(new_frame, font=SMALL_TEXT_FONT, bg=frame_color,
                               text="Risk (out of 1,000,000):")
        step3c.grid(row=starting_row+1, column=3, padx=5, pady=2, sticky="NE")
        risk_num = EntryWithPlaceholder(new_frame, placeholder="Enter a risk threshold >= 1")
        risk_num["width"] = 30

        if risk is not None:
            risk_num.set_value(risk)
        risk_num.grid(row=starting_row+1, column=4, pady=3, sticky="NW")

        remove_btn = tk.Button(new_frame, text="Remove", bg='lightgrey', relief='solid', borderwidth=1,
                              command=partial(self.remove_config, config), font=SMALL_TEXT_FONT)
        remove_btn.grid(row=starting_row, column=5, rowspan=2, sticky='E', padx=15, pady=5)

        self.next_config += 1

