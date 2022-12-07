from dataclasses import dataclass
from multiprocessing import Queue, Lock
from queue import Empty

QUERY = "query"
INSERT = "insert"
PRE_REMOVE = "pre_remove"
FINAL_REMOVE = "final_remove"
DEFAULT_IMAGE =  r"resources\default.png"


@dataclass
class QueryObject:
    images: list = None
    name: str = ""
    credentials: str = ""
    command: str = QUERY

@dataclass
class ResponseObject:
    unique_id: str = ""
    name: str = ""
    added: str = ""
    last_query: str = ""
    searches: str = ""
    credentials: str = ""
    confidence: str = ""
    image: str = DEFAULT_IMAGE

@dataclass
class ErrorObject:
    msg: str = "communication error!"


class MessageHandler:
    def __init__(self):
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.lock = Lock()

    def send_request(self, query):
        self.in_queue.put(query)

    def wait_response(self):
        try:
            response = self.out_queue.get(block=False)
        except Empty:
            response = None
        return response
