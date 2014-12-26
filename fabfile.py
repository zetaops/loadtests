# -*-  coding: utf-8 -*-
from __future__ import with_statement
from time import sleep
from fabric.api import *
from fabric.contrib.project import rsync_project

# HOST = '192.168.56.102' #VM
HOST = '148.251.192.21'

PORT = "22"
EXCLUDE = "*.log *.map examples *.coffee *.db *.pyc *~ .idea .git *.png".split(' ')

env.hosts = [HOST]
env.port = PORT

WORK_DIR = '/home/evren/'

RUN_CMD = {
    'gunicorn': "{nohup} gunicorn --statsd-host 127.0.0.1:8125 -w {workers} -D --timeout 1000 app:app {debug} "
                "-t {threads} -b {host}:{port} --backlog 2048 {gevent} {xtra}",

    'uwsgi': "uwsgi -T -i {debug} --http {host}:{port} --file app.py --callable app -p {workers} -d true "
             "--stats /tmp/statsock --pidfile /tmp/uwsgimaster.pid {gevent} {xtra}"
}

GEVENT_PARAMS = {
    "gunicorn":" -k gevent --worker-connections %s ",
    "uwsgi":" --gevent %s ",
}

DEBUG_PARAMS = {
    'gunicorn': "--log-level error --debug --error-logfile /tmp/gunicorn_error.log",
    'uwsgi': "--catch-exceptions --logger file:///tmp/uwsgi.log"
}


PROD_PARAMS = {
    "gunicorn": '',
    'uwsgi': '-L'
}

GRACEFUL_KILL_CMD = {
    "gunicorn": "killall gunicorn",
    "uwsgi": "uwsgi --stop /tmp/uwsgimaster.pid"
}


def sync():
    rsync_project(WORK_DIR, exclude=EXCLUDE)


def kill(server, bequiet=False):
    with cd(WORK_DIR + "pyexp/flask"):
        run(GRACEFUL_KILL_CMD[server], quiet=bequiet, warn_only=not bequiet)
        run("killall wrk", quiet=bequiet, warn_only=not bequiet)
        sleep(1)
        run("killall -9 wrk", quiet=bequiet, warn_only=not bequiet)
        run("killall -9 %s" % server, quiet=bequiet, warn_only=not bequiet)


def load(concurrency=5, duration=60,  host=HOST, port='8000', uri='/load'):
    test_threads = (int(concurrency) / 10) + 1
    run("wrk -d %s -t %s -c %s http://%s:%s%s" % (duration, test_threads, concurrency, host, port, uri))


def test(server="gunicorn", host=HOST, port='8000', gevent=0, concurrency=5, workers=4, threads=5, debug=False,
         nohup=False, duration=60, count='', xtra=""):

    if count and gevent:
        print("PyCounters and gevent can not be used together")
        return

    sync()
    kill(server, True)

    options = {'nohup': 'nohup ' if nohup else '',
               'workers': workers,
               'debug': DEBUG_PARAMS[server] if debug else PROD_PARAMS[server],
               'host': host,
               'port': port,
               'threads': threads,
               'xtra': xtra,
               'gevent': GEVENT_PARAMS[server] % gevent if gevent else "",
               }

    with cd(WORK_DIR + "pyexp/flask"):
        runcmd = RUN_CMD[server].format(**options)
        use_pycounters = '1' if count else ''
        with shell_env(SERVER_SOFTWARE=server, USE_PYCOUNTERS=use_pycounters,
                       ASYNC_MODE=str(gevent), TCONCURRENCY=concurrency,
                       SERVER_CMD=runcmd):
            run(runcmd, warn_only=True)
    sleep(1)
    load(concurrency, duration, host=host, port=port)

