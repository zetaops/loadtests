from time import sleep
import pytest
import os
from multiprocessing.connection import Listener
from thread import start_new_thread
# from gevent.thread import start_new_thread
from loadtests.stats.stats_generator import StatsGenerator


__author__ = 'Evren Esat Ozkan'



def test_get_server_name_from_environ():
    server_name = 'gunicorn'
    os.environ['SERVER_SOFTWARE'] = server_name
    sg = StatsGenerator()
    assert server_name == sg.server_process_name

def test_get_server_name_from_args():
    server_name = 'gunicorn'
    sg = StatsGenerator(server_name)
    assert server_name == sg.server_process_name


