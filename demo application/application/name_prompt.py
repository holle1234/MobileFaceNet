from tkinter import *
from functools import partial
from .utils import center_top_level


class NamePrompt(Toplevel):
    def __init__(self, master, callback, *args, **kwargs):
        super(NamePrompt, self).__init__(master, *args, **kwargs)

        # callback for confirmation button
        self.callback = callback

        # init popup
        self.attributes('-topmost', 'true')
        self.resizable(False, False)
        self.title("Create Face-Id")

        # track changes to this variable
        self.input = StringVar()
        self.input.trace("w", lambda *_, var=self.input: self.on_entry(var))
        self.b = self.create_gui()
        self.protocol("WM_DELETE_WINDOW", partial(self.on_callback, cancel=True))

    def create_gui(self):
        frame = Frame(self)
        frame.grid(padx=5, pady=5)
        Label(frame, text="Name", font=("ariel", 13)).grid(row=0, column=0, padx=2)
        Entry(frame, width=30, font=("ariel", 15), textvariable=self.input).grid(row=0, column=1)
        confirm_but = Button(frame, text="Confirm", state="disabled", command=self.on_callback)
        confirm_but.grid(row=0, column=2, padx=2)

        # window position to center
        center_top_level(self)

        return confirm_but

    @staticmethod
    def is_valid_name(name):
        text = name.replace(" ", "")
        text_len = len(text)
        if text_len < 3 or text_len > 40:
            return False
        return True

    def on_entry(self, var):
        if not self.is_valid_name(var.get()):
            self.b["state"] = "disabled"
        else:
            self.b["state"] = "normal"

    def on_callback(self, cancel=False):
        # its possible that user closed the window early
        name, state = self.input.get(), 0
        if cancel or not self.is_valid_name(name):
            name, state = None, -1
        if callable(self.callback):
            self.callback(name=name, state=state)
        self.destroy()