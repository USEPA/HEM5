import tkinter as tk
import PIL.Image
import os
from tkinter import messagebox
from com.sca.hem4.gui.Styles import TEXT_FONT, MAIN_COLOR, TAB_COLOR, HIGHLIGHT_COLOR, CHECKBOX_COLOR


class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.main_color = MAIN_COLOR
        self.tab_color = TAB_COLOR
        self.highlightcolor = HIGHLIGHT_COLOR
        self.checkbox_color = CHECKBOX_COLOR

    def add_margin(self, pil_img, top, right, bottom, left):
        width, height = pil_img.size
        new_width = width + right + left
        new_height = height + top + bottom
        result = PIL.Image.new(pil_img.mode, (new_width, new_height))
        result.paste(pil_img, (left, top))
        return result

    def color_config(self, widget1, widget2, container, color, event):

        widget1.configure(bg=color)
        widget2.configure(bg=color)
        container.configure(bg=color)

    def fix_config(self, widget1, widget2, previous):

        try:
            widget1.configure(bg=self.tab_color)
            widget2.configure(bg=self.tab_color)

            if len(previous) > 0:

                for i in previous:
                    i.configure(bg=self.main_color)

        except:
            pass

    # Event handlers for porting instructions
    def add_instructions(self, placeholder1, placeholder2):

        #Dynamic instructions place holder
        global instruction_instance
        self.instruction_instance = tk.StringVar(placeholder1)
        self.instruction_instance.set(" ")
        self.instruction_instance.set(" ")
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
        self.instruction_instance.set(" ")
        self.instruction_instance.set(" ")

    # general function for browsing instructions
    def browse(self, location):
        """
        Function looks up text file with instructions for specified input
        browse buttons
        """
        global instruction_instance
        self.read_inst = open(location, 'r')
        self.instruction_instance.set(self.read_inst.read())
        self.instruction_instance.set(self.read_inst.read())
        self.instruction_instance.set(self.read_inst.read())

    def show(self):
        self.lift()

    def disabled_message(self, event):
        """ Pop up for user when trying to run census updatae and hem4 modelling
            concurrently
        """
        messagebox.showinfo("Application Running","This feature is disabled while the application is running.")

    # File upload helpers
    def is_valid_extension(self, filepath):
        """
        Function checks to make sure excel/csv files are selected for inputs
        """
        extensions = [".xls", ".xlsx", ".XLS", ".csv", ".CSV"]
        return any(ext in filepath for ext in extensions)

    def openFile(self, filename):
        """
        This function opens file dialogs for uploading inputs
        """

        if not filename:
            # upload was canceled
            print("Canceled!")
            return None
        elif not self.is_valid_extension(filename):
            messagebox.showinfo("Invalid file format",
                                "Not a valid file format, please upload an excel/csv file as per the instructions.")
            return None
        else:
            return os.path.abspath(filename)