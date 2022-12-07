from tkinter import *
from tkinter.messagebox import showinfo
from communication import *
from server import Predictor
from .camera import Camera
from .name_prompt import NamePrompt
from .results_pop import ResultsPop
from functools import partial


class Main(Tk):
    def __init__(self, **kwargs):
        super(Main, self).__init__()

        self.data_path = kwargs.get("data_path", "data")
        self.confidence_threshold = kwargs.get("confidence_threshold", 0.85)

        self.image_container = []
        self.msg_handler = MessageHandler()
        self.camera, self.buttons = self.create_gui()

        self.prediction_process = self.create_prediction_process()
        self.is_ready_for_predictions()

    def create_gui(self):
        self.resizable(False, False)
        self.title('FaceRecognition')
        self.bind('<Escape>', lambda e: self.close)

        cam = Camera(self, self.image_container)
        cam.grid(row=0, column=1, rowspan=3, sticky="nsew")
        query = Button(self, text="Login", state="disabled", command=self.db_query)
        query.grid(row=0, column=0, sticky="nsew")
        insert = Button(self, text="Create", state="disabled", command=self.db_insert)
        insert.grid(row=1, column=0, sticky="nsew")
        remove = Button(self, text="Delete", state="disabled", command=self.db_remove)
        remove.grid(row=2, column=0, sticky="nsew")
        return cam, (query, insert, remove)

    def create_prediction_process(self):
        # init background process that handles database
        process = Predictor(self.data_path,
                            self.msg_handler,
                            th=self.confidence_threshold,
                            daemon=True)
        process.start()
        return process

    def is_ready_for_predictions(self):
        # wait for background process to initialize
        if self.prediction_process.loaded.value:
            for button in self.buttons:
                button["state"] = "normal"
        else:
            self.after(100, self.is_ready_for_predictions)

    def db_query(self, state=0):
        if state == 0:
            # start collecting images
            self.start_recognizer()
            self.after(1000, self.db_query, 1)
        elif state == 1:
            # stop collecting images and send them to process
            self.camera.stop_capture()
            query = QueryObject(images=self.image_container, command=QUERY)
            self.msg_handler.send_request(query)
            self.after(100, self.db_query, 2)
        elif state == 2:
            # show results in popup window
            response = self.msg_handler.wait_response()
            if response:
                ResultsPop(self, self.is_ready_for_predictions, response)
            else:
                self.after(100, self.db_query, 2)

    def db_insert(self, name=None, state=0):
        if state == -1:
            # cancel event, user cancelled
            self.camera.stop_capture()
            self.is_ready_for_predictions()
        elif not name and state == 0:
            # open name NamePrompt first and relay back the input
            self.disable_buttons()
            NamePrompt(self, callback=self.db_insert)
        elif state == 0:
            # start collecting images
            self.start_recognizer()
            self.after(1000, self.db_insert, name, 1)
        elif state == 1:
            # stop collecting images and send them to process
            self.camera.stop_capture()
            query = QueryObject(images=self.image_container, name=name, command=INSERT)
            self.msg_handler.send_request(query)
            self.after(100, self.db_insert, name, 2)
        elif state == 2:
            # show results in popup window
            response = self.msg_handler.wait_response()
            if response:
                ResultsPop(self, self.is_ready_for_predictions, response)
            else:
                self.after(100, self.db_insert, name, state)

    def db_remove(self, state=0, creds=None):
        if state == 0:
            # start collecting images
            self.start_recognizer()
            self.after(1000, self.db_remove, 1)
        elif state == 1:
            # stop collecting images and send them to process
            self.camera.stop_capture()
            query = QueryObject(images=self.image_container, command=PRE_REMOVE)
            self.msg_handler.send_request(query)
            self.after(100, self.db_remove, 2)
        elif state == 2:
            # if record is found ask to delete otherwise break loop
            response = self.msg_handler.wait_response()
            if response:
                if response.unique_id:
                    callback = partial(self.db_remove, state=3, creds=response.credentials)
                else:
                    callback = self.is_ready_for_predictions
                ResultsPop(self, callback, response)
            else:
                self.after(100, self.db_remove, 2)
        elif state == 3 and creds is not None:
            query = QueryObject(command=FINAL_REMOVE, credentials=creds)
            self.msg_handler.send_request(query)
            self.after(100, self.db_remove, 4)
        elif state == 4:
            # show query results in popup window
            response = self.msg_handler.wait_response()
            if response:
                showinfo(title="Removal Status", message="Record removed from the database!")
                self.is_ready_for_predictions()
            else:
                self.after(100, self.db_remove, 4)

    def start_recognizer(self):
        # start to collect images
        self.image_container.clear()
        self.camera.start_capture()
        self.disable_buttons()

    def disable_buttons(self):
        for button in self.buttons:
            button["state"] = "disabled"

    def close(self):
        # close application resources
        self.camera.cap.release()
        self.quit()
        self.prediction_process.terminate()

