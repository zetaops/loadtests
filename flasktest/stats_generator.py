from collections import defaultdict
from json import loads,dumps
import socket
from thread import start_new_thread
from time import sleep, time
import psutil
import os
from multiprocessing.connection import Client


class StatsGenerator:
    """
    This class collects rps (request per second), memory and cpu usage stats for the current wsgi server
    We use psutils for memory and cpu usage.
    For Gunicorn and uWSGI, we are collecting data directly from webservers native channels.
    Otherwise, we use PyCounters which isn't  compatible with gevent,
    so it will crash the server when used with async cores.
    """

    def __init__(self, server_process_name=None):
        self.server_process_name = server_process_name or   self.get_server_name()
        self.count_method = "pycounters" if os.environ.get("USE_PYCOUNTERS") else self.server_process_name
        init_stats_collector = getattr(self, 'init_%s_stats' % self.count_method, None)
        if init_stats_collector:
            init_stats_collector()
        self.get_rps = getattr(self, 'get_rps_from_%s' % self.count_method, self.get_rps_from_pycounters)
        self.server_data = {
            "concurrency": os.environ.get("TCONCURRENCY"),
            "serverCommand": os.environ.get("SERVER_CMD"),
            "debugMode": 'Yes' if os.environ.get("DEBUGMODE", '') else 'No',
            "RPSCountingMethod": self.count_method,
        }


    def init_gunicorn_stats(self):
        # starting an udp server to collect gunicorn stats
        self.req_per_sec = defaultdict(int)
        start_new_thread(self.gunicorn_statsd, ())


    def init_uwsgi_stats(self):
        self.last_tot_time = time()
        self.last_reqnumber_per_worker = defaultdict(int)
        self.last_reqnumber_per_core = defaultdict(int)


    @staticmethod
    def get_server_name():
        natively_supported = ['gunicorn', 'uwsgi']
        for s in natively_supported:
            if s in os.environ.get('SERVER_SOFTWARE').lower():
                return s


    def get_server_type(self):
        return self.server_process_name

    def get_rps(self):
        # this method should be overriden at init stage with one of the apopriate get_rps_from_X methods
        raise NotImplemented

    @staticmethod
    def get_rps_from_pycounters():
        # gets the "request per second" data from counter server via
        # multiprocessing Client from Listener which runs in a thread
        # fired from possibly another webserver process
        try:
            rps_client = Client("/tmp/rpssock")
            rps = rps_client.recv_bytes()
            rps_client.close()
        except:
            rps = 0
        return rps


    def get_process_stats(self):
        # returns cumulative cpu and memory usage of the self.server_process_name
        try:
            mem, cpu = zip(*[(p.memory_info().rss, p.cpu_percent())
                             for p in psutil.process_iter()
                             if p.name() == self.server_process_name])
            return sum(mem) / 1024, sum(cpu) / len(cpu)
        except Exception, e:
            print e

    FIRST_ITERATION = True

    def generate_stats(self):
        # json stat generator for realtime load visiulation
        # inits the json list and sends the server information to the client at first iteration

        while 1:
            if not self.FIRST_ITERATION:
                sleep(0.5)
                try:
                    mem, cpu = self.get_process_stats()
                    yield '%s,' % dumps({"RPS": self.get_rps(), "MEM":mem, "CPU": cpu})
                except Exception, e:
                    yield '{"error": "%s"},' % e
            else:
                self.FIRST_ITERATION = False
                yield '{"rp":[%s,' % dumps(self.server_data)


    def get_rps_from_gunicorn(self):
        return self.req_per_sec.get(int(time()) - 2, 0)

    def gunicorn_statsd(self):
        # gunicron wants to send it's stats to a statd server
        # so we acting like one, listening and calculating rps, in a very rough way!
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 8125))
        while 1:
            if ".status.200" in s.recvfrom(100)[0]:
                self.req_per_sec[int(time())] += 1

    def get_rps_from_uwsgi(self):
        # uwsgi gives stats in JSON format over a unixsocket
        # this method gets data and calculates total rps
        # partly taken from: https://github.com/unbit/uwsgitop/blob/master/uwsgitop
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect('/tmp/statsock')
        jsondata = ''
        while 1:
            d = s.recv(4094)
            if len(d) < 1:
                break
            jsondata += d
        dd = loads(jsondata)
        rps_per_worker = {}
        s.close()
        dt = time() - self.last_tot_time
        total_rps = 0
        for worker in dd['workers']:
            wid = worker['id']
            curr_reqnumber = worker['requests']
            last_reqnumber = self.last_reqnumber_per_worker[wid]
            rps_per_worker[wid] = (curr_reqnumber - last_reqnumber) / dt
            total_rps += rps_per_worker[wid]
            self.last_reqnumber_per_worker[wid] = curr_reqnumber

        self.last_tot_time = time()
        return total_rps
