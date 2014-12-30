from time import sleep

__author__ = 'Evren Esat Ozkan'
import pytest
import os
os.environ['USE_PYCOUNTERS'] = '1'
from multiprocessing.connection import Listener
from thread import start_new_thread
from loadtests.stats.stats_generator import StatsGenerator


def mock_pycount_reporter(value):
    conn = Listener("/tmp/rpssock").accept()
    conn.send_bytes(value)
    conn.close()



def test_get_rps_from_pycounter():
    test_value = '999'
    start_new_thread(mock_pycount_reporter, (test_value,))
    sleep(0.5)
    sg = StatsGenerator('gunicorn')
    assert test_value == sg.get_rps()

