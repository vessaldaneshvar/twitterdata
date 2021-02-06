from django.apps import AppConfig
from multiprocessing import Process
from django import db

class StreamTwitterDataProcess(Process):
    def __init__(self):
        super().__init__()
        self.daemon = True
    
    def run(self):
        from .tasks import get_stream_data_and_save_users

        db.connections.close_all()

        get_stream_data_and_save_users()

        

class DataConfig(AppConfig):
    name = 'data'

    def ready(self):
        stream = StreamTwitterDataProcess()
        stream.start()
