from tkinter import *
from tkinter import ttk
from PIL.ImageTk import PhotoImage
from communication import ResponseObject
from cv2.cv2 import cvtColor, COLOR_BGR2RGBA
from PIL.Image import fromarray
from .utils import center_top_level


class ResultsPop(Toplevel):
    def __init__(self,master, callback, results:ResponseObject, *args, **kwargs):
        super(ResultsPop, self).__init__(master, *args, **kwargs)

        # init popup
        self.attributes('-topmost', 'true')
        self.resizable(False, False)

        # callback for closing button
        self.callback = callback

        # unpack data
        self.name = self.format_name(results.name)
        self.unique_id = results.unique_id or f"{'-':^30}"
        self.last_query = results.last_query or f"{'-':^30}"
        self.added = results.added or f"{'-':^30}"
        self.searches = results.searches or f"{'-':^30}"
        self.confidence = results.confidence or f"{'-':^30}"

        # load image
        frame = cvtColor(results.image, COLOR_BGR2RGBA)
        self.image = PhotoImage(image=fromarray(frame))

        self.protocol("WM_DELETE_WINDOW", self.on_callback)
        self.create_gui()
        center_top_level(self)

    @staticmethod
    def format_name(name):
        name = name if len(name) < 30 else f"{name[:27]}..."
        return name or f"{'-':^30}"

    def create_gui(self):
        # image
        Label(self, image=self.image).grid(row=0, column=0, rowspan=7, padx=(5,5), pady=(5,2))
        Label(self, text=self.name).grid(row=7, column=0)

        # info
        headers = ['Added:', 'Last Login:', 'Searches:', 'Id:', 'Confidence:']
        data = [self.added, self.last_query, self.searches, self.unique_id, self.confidence]

        for ind, (header, value) in enumerate(zip(headers, data)):
            # header
            label = ttk.Label(self, text=header)
            label.grid(column=1, row=ind, sticky=W, padx=5, pady=2)

            # value
            label = ttk.Label(self, text=value)
            label.grid(column=2, row=ind, sticky=W, padx=5, pady=2)

        but = Button(self, text="Ok", command=self.on_callback, activebackground="#BEBEBE", bg="#BEBEBE")
        but.grid(row=7, column=1, columnspan=2, sticky="nsew", padx=2, pady=2)
        self.grid()

    def on_callback(self):
        if callable(self.callback):
            self.callback()
        self.destroy()
