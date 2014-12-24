import fcntl
import os
import json
from pycounters.reporters import BaseReporter

__author__ = 'Evren Esat Ozkan'

class MemoryJSONFileReporter(BaseReporter):
    """
        Reports to a file in a JSON format.

    """

    def __init__(self, fd=None):
        """
            :param output_file: a file name to which the reports will be written.
        """
        super(MemoryJSONFileReporter, self).__init__()
        self.fd = fd

    def output_values(self, counter_values):
        if counter_values['requests_frequency'] > 0:
            self.fd.append(counter_values)
