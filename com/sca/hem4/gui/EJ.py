from com.sca.hem4.gui.Page import Page
import tkinter as tk
from com.sca.hem4.gui.Styles import TEXT_FONT


class EJ(Page):
    def __init__(self, nav, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

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
