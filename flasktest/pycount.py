__author__ = 'Evren Esat Ozkan'
from pycounters import register_counter, counters, register_reporter, start_auto_reporting, \
    configure_multi_process_collection #, report_start_end
from pycounters.shortcuts import occurrence
from multiprocessing.connection import Listener
from pycounters.reporters import BaseReporter, JSONFileReporter


class SocketReporter(BaseReporter):
    """
        Serves reports using multiprocessing.Listener (to StatsGenerator)
    """

    def __init__(self, RP=None):
        """
            :param output_file: a file name to which the reports will be written.
        """
        super(BaseReporter, self).__init__()
        # start_new_thread(self.serv_results, ())

    def serv_results(self):
        listener = Listener("/tmp/rpssock")
        conn = listener.accept()
        conn.send_bytes(self.RPS)
        conn.close()

    def output_values(self, counter_values):
        #not sure but probably this method will be called from PyCounter's "leader" collector process
        if counter_values['requests_frequency'] and counter_values['requests_frequency'] > 0:
            self.RPS = str(counter_values['requests_frequency'])
            self.serv_results()

rps_counter = counters.FrequencyCounter("requests_frequency", window_size=2)  # not working when set to 1
register_counter(rps_counter)
reporter = SocketReporter()
# json_reporter = JSONFileReporter("/tmp/pyc.json")
# register_reporter(json_reporter)
register_reporter(reporter)
start_auto_reporting(seconds=1)
configure_multi_process_collection()
