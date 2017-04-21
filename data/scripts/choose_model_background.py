'''
This script is used to run our choose model module as a background job
'''
import django_rq
from .choose_model import run as model_run

def run():
    '''
    Adds choose_model job to our Django Redis Queue
    '''
    print("Starting run from choose_model_background")
    queue = django_rq.get_queue('high')
    print("Got queue")
    queue.enqueue(model_run, timeout = 25200)
    print("Enqueued job.")
