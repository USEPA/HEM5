from com.sca.hem4.gui.Page import Page
import tkinter as tk
from com.sca.hem4.gui.Styles import TEXT_FONT
from tkinter import scrolledtext


class Log(Page):

    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.nav = nav

        container = tk.Frame(self, bg=self.tab_color, bd=2)
        container.pack(side="top", fill="both", expand=True)

        # Adding a Textbox Entry widget
        self.scr = scrolledtext.ScrolledText(container, wrap=tk.WORD, width=1000, height=1000, font=TEXT_FONT)
        self.scr.configure(cursor='none')
        self.scr.pack(expand=1, fill="both")
        self.scr.bind("<Button-1>", self.interfere)

    def interfere(self, event):
        print("Block interruption")