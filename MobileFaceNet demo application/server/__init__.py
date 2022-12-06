from communication import *
from math_utils import normalized_sum_array, preprocess_images
from multiprocessing import Process, Value
from numpy import vstack, expand_dims
from cv2.cv2 import cvtColor, COLOR_BGR2RGB
from pathlib import Path


class Predictor(Process):

    def __init__(self, data_path, msg_handler, th=0.85, *args, **kwargs):
        super(Predictor, self).__init__(*args, **kwargs)
        self.data_path = data_path
        self.confidence_threshold = th

        # data in and out queues
        self.in_q = msg_handler.in_queue
        self.out_q = msg_handler.out_queue
        self.lock = msg_handler.lock

        # variables to be set inside the process
        self.model = None
        self.face_db = None
        self.face_aligner = None
        self.waiting_removal = {}

        # this variable must be shared with parent process
        self.loaded = Value("b", False)

    def align_faces(self, images):
        aligned = []
        for image in images:
            image = cvtColor(image, COLOR_BGR2RGB)
            ret, face = self.face_aligner.align_face(image)
            if ret:
                aligned.append(expand_dims(face, 0))
        return aligned

    def create_searchable(self, images):
        images = self.align_faces(images)
        if len(images) < 10:
            return None, None

        pre_images = preprocess_images(vstack(images))
        arrays = self.model(pre_images, training=False)
        pointer_array = normalized_sum_array(arrays)
        return pointer_array, images[0][0]

    def find_from_db(self, a:QueryObject):
        results, _ = self.create_searchable(a.images)
        return self.face_db.query(results)

    def insert_to_db(self, a:QueryObject):
        array, sample = self.create_searchable(a.images)
        # image is in RGB format -> convert before saving
        sample = cvtColor(sample, COLOR_BGR2RGB)
        return self.face_db.insert(array, a.name, sample)

    def pre_remove_from_db(self, a:QueryObject):
        db_resp = self.find_from_db(a)
        if db_resp.name:
            self.waiting_removal[db_resp.credentials] = db_resp.unique_id
        return db_resp

    def remove_from_db(self, a:QueryObject):
        credentials = a.credentials
        key = int(self.waiting_removal.get(credentials, None))
        return self.face_db.remove(key)

    def handle_message(self, message):
        if not isinstance(message, QueryObject):
            response = ErrorObject("Query is not a QueryObject!")
            self.out_q.put(response)
        elif message.command == QUERY:
            response = self.find_from_db(message)
            self.out_q.put(response)
        elif message.command == INSERT:
            response = self.insert_to_db(message)
            self.out_q.put(response)
        elif message.command == PRE_REMOVE:
            response = self.pre_remove_from_db(message)
            self.out_q.put(response)
        elif message.command == FINAL_REMOVE:
            response = self.remove_from_db(message)
            self.out_q.put(response)
        else:
            response = ErrorObject("Query command not recognized!")
            self.out_q.put(response)

    def run(self):
        # load these here so they wont become shared with parent process
        from database import DataBase
        from face_extract import FaceAligner
        from keras_model import get_model

        self.model = get_model()
        self.face_db = DataBase(self.data_path, self.confidence_threshold)
        self.face_aligner = FaceAligner()

        # set loaded value to True so GUI can start to feed data
        with self.loaded.get_lock():
            self.loaded.value = True

        # Run infinitely
        while True:
            message = self.in_q.get()
            self.handle_message(message)
