from tkinter import *
from PIL.Image import fromarray
from PIL.ImageTk import PhotoImage
import cv2


class Camera(Label):
    def __init__(self, master, image_container, *args, **kwargs):
        super(Camera, self).__init__(master=master, *args, **kwargs)
        self.image_container = image_container
        self.face_capture = False
        self.n_captured = 0

        w = kwargs.get("width", 800)
        h = kwargs.get("height", 800)
        source = kwargs.get("source", 0)

        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self.refresh_frame()

    def refresh_frame(self):
        try:
            ret, frame = self.cap.read()
        except KeyboardInterrupt:
            self.cap.release()
        else:
            if not ret:
                return None

            if self.face_capture:
                self.image_container.append(frame)
                self.n_captured += 1

            cv2.flip(frame, 1, frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = fromarray(frame)

            tinker_img = PhotoImage(image=img)
            self.imgtk = tinker_img
            self.configure(image=tinker_img)
            self.after(10, self.refresh_frame)

    def start_capture(self):
        self.n_captured = 0
        self.face_capture = True

    def stop_capture(self):
        self.face_capture = False

