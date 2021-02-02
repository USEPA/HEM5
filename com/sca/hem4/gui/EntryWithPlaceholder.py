import tkinter as tk


class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', name=None):

        self.sv = tk.StringVar()

        super().__init__(master, textvariable=self.sv, name=name)
        self.sv.trace("w", lambda name, index, mode, sv=self.sv: self.handle_change(sv))

        self.text_value = ""

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def handle_change(self, sv):
        self.text_value = sv.get()

    def put_placeholder(self):
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        self.text_value = ""
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

    def set_value(self, value):
        self.delete(0, tk.END)
        self.insert(0, value)
        self.text_value = value
        self['fg'] = self.default_fg_color

    def get_text_value(self):
        return self.text_value
