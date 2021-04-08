from com.sca.hem4.gui.Page import Page
import tkinter as tk
from com.sca.hem4.gui.Styles import TITLE_FONT, TEXT_FONT
import PIL.Image
from PIL import ImageTk


class Start(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        container = tk.Frame(self, bg=self.tab_color, bd=2)
        container.pack(side="top", fill="both", expand=True)

        self.s1 = tk.Frame(container, width=600, height=50, bg=self.tab_color)
        self.s2 = tk.Frame(container, width=600, height=50, bg=self.tab_color)
        self.s3 = tk.Frame(container, width=600, height=50, bg=self.tab_color)
        self.s4 = tk.Frame(container, width=600, height=50, bg=self.tab_color)
        self.s5 = tk.Frame(container, width=600, height=50, bg=self.tab_color)

        #grid layout for main inputs
        self.s1.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.s1.columnconfigure(2, weight=1)

        self.s2.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.s2.columnconfigure(2, weight=1)

        self.s3.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.s3.columnconfigure(2, weight=1)

        self.s4.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.s4.columnconfigure(2, weight=1)

        self.s5.grid(row=5, column=0, columnspan=2, sticky="nsew")
        self.s5.columnconfigure(2, weight=1)

        #title in first grid space
        title1 = tk.Label(self.s1, text="HEM4", font=TITLE_FONT, bg=self.tab_color)
        title1.grid(row=0, column=2, pady=20)

        title2 = tk.Label(self.s1, text="Version 4.1 ", font=TEXT_FONT, bg=self.tab_color)
        title2.grid(row=1, column=2, pady=20)

        #some information
        prepared_for = tk.Label(self.s4, text="Prepared for: \nAir Toxics" +
                                              " Assessment Group \nU.S. EPA \nResearch Triangle Park, NC 27711",
                                font=TEXT_FONT, bg=self.tab_color)
        prepared_for.grid(row=1, column=0, padx=60)


        image1 = ImageTk.PhotoImage(PIL.Image.open('images\smokestack.jpg').resize((220,200)))
        ione = tk.Label(self.s3, image=image1)
        ione.image = image1 # keep a reference!
        ione.grid(row=1, column=1, padx=70, sticky='W', pady=20)

        prepared_by = tk.Label(self.s4, text="Prepared by: \nSC&A Incorporated\n" +
                                             "1414 Raleigh Rd, Suite 450\nChapel Hill, NC 27517",
                               font=TEXT_FONT, bg=self.tab_color)
        prepared_by.grid(row=1, column=2, padx=10, sticky='E')


        img = PIL.Image.open('images\\usersguides.jpg')
        img = img.resize((250,200), PIL.Image.ANTIALIAS)
        image2 = ImageTk.PhotoImage(img)
        itwo = tk.Label(self.s3, image=image2)
        itwo.image = image2 # keep a reference!
        itwo.grid(row=1, column=2, padx=10, sticky='E', pady=20)