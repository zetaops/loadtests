# -*-  coding: utf-8 -*-
from __future__ import with_statement
import time
from fabric.api import env, run, cd
from fabric.context_managers import shell_env
from fabric.contrib.project import rsync_project
import webbrowser
from fabric import utils

# Set your access credentials in a local_settings.py file
# or just change the contents of except block.
try:
    from local_settings import *
except ImportError:
    HOST = 'localhost'
    PORT = "22"
    WORKING_DIR = ''
    USER = ''

if USER:
    env.user = USER
env.hosts = [HOST]
env.port = PORT
WORK_DIR = WORKING_DIR if WORKING_DIR else '/home/%s/' % (env.user or env.local_user)

SERVERS = {
    'gunicorn': {
        'run': "{nohup} gunicorn {serv_method}  -w {workers} -D --timeout 1000 app:app {debug} "
               " --backlog 2048 {threads} {gevent} {stats} {xtra}",
        'gevent': " -k gevent --worker-connections %s ",
        'debug': "--log-level error --debug --error-logfile /tmp/gunicorn_error.log",
        'prod': '',
        'threads': '--threads %s',
        'grace_kill': 'killall gunicorn',
        'stats': '--statsd-host 127.0.0.1:8125',
        'proxy': '-b unix:/tmp/gunicorn_testing.sock',
        'proxy_port': '8002',
        'direct': '-b %s:%s',

    },
    'uwsgi': {
        'run': "uwsgi -i {debug} {serv_method} --file app.py --callable app -p {workers} -d true "
               " --pidfile /tmp/uwsgimaster.pid {threads} {gevent} {stats} {xtra}",
        'gevent': " --gevent %s ",
        'debug': "--catch-exceptions --logger file:///tmp/uwsgi.log",
        'prod': '-L',
        'threads': '-T --threads %s',
        'grace_kill': 'uwsgi --stop /tmp/uwsgimaster.pid',
        'stats': '--stats /tmp/statsock',
        'proxy': '--socket /tmp/uwsgi_testing.sock  --chmod-socket=666',
        'proxy_port': '8001',
        'direct': '--http %s:%s',
    }
}


def sync():
    """
    syncs the files with test machine (to home dir. by default)
    """
    rsync_project(WORK_DIR, local_dir="./flasktest",
                  exclude="*.log *.map fabfile *.pyc *~ .idea .git *.png".split(' '))


def kill(server, bequiet=False):
    """
    first we politely ask to stop, then throw a  SIGKILL signal, just in case...
    """
    with cd(WORK_DIR + "flasktest"):
        run(SERVERS[server]['grace_kill'], quiet=bequiet, warn_only=not bequiet)
        run("killall wrk", quiet=bequiet, warn_only=not bequiet)
        time.sleep(1)
        run("killall -9 wrk", quiet=bequiet, warn_only=not bequiet)
        run("killall -9 %s" % server, quiet=bequiet, warn_only=not bequiet)


def load(concurrency=5, duration=60, host=HOST, port='8000', uri='/load'):
    """
    this will stress the server via wrk load testing tool.
    number of threads are calculated based on selected concurrency ( concurrency/10 + 1 )
    """
    test_threads = (int(concurrency) / 10) + 1
    run("wrk -d %s -t %s -c %s http://%s:%s%s" % (duration, test_threads, concurrency, host, port, uri))


def test(server="gunicorn", host=HOST, port='8000', gevent='', concurrency='50', workers='', threads='', debug='',
         nohup='', web='', duration='40', count='', proxy='', xtra=''):
    """
    deploy files, run the selected wsgi server and start load testing.

    These uWSGI specific commands may affect the performance and can be tweaked via "xtra" field.
    --thunder-lock
    --master

    server: server name to test. Should be 'gunicorn' or 'uwsgi'
    host: host address to connect and start the test. default is same as fabric HOST
    port: web server port
    gevent: number of async (gevent) cores
    proxy: run behind nginx. use the config files located under the nginx directory
    concurrency: test client concurrency
    workers: number of server processes, default: cpu_count * 2 /1
    threads: number of server threads
    debug: set any value to enable debugging flags
    web: set any value to open monitoring page during load test
    duration: test duration (wrk parameter)
    count: set any value to use PyCounters for calculation of requests per second. (do not use with gevent)
    nohup: some OS'es unable to daemonize the server without this
    xtra: set any params for passing to server run command
    """
    srv = SERVERS[server]

    if count and gevent:
        utils.error("PyCounters and gevent can not be used together")
    if proxy and port != '8000':
        utils.warn("Please be sure that your nginx configuration (%s.conf) "
             "reflects to your current port setting: %s" % (server, port))

    sync()
    kill(server, True)
    options = {
        'nohup': 'nohup ' if nohup else '',
        'workers': workers or run("python -c 'import multiprocessing; print multiprocessing.cpu_count() * 2 + 1'"),
        'debug': srv['debug'] if debug else srv['prod'],
        'gevent': srv['gevent'] % gevent if gevent else "",
        'stats': srv['stats'] if not count else '',
        'threads': srv['threads'] % threads if threads else '',
        'serv_method': srv['proxy'] if proxy else srv['direct'] % (host, port),
        'xtra': xtra,
    }

    with cd(WORK_DIR + "flasktest"):
        runcmd = srv['run'].format(**options)
        use_pycounters = '1' if count else ''
        # server_software will be used for rps calculation,
        # other env vars will be passed to the web client
        with shell_env(SERVER_SOFTWARE=server, USE_PYCOUNTERS=use_pycounters,
                       ASYNC_MODE=str(gevent), TCONCURRENCY=concurrency,
                       SERVER_CMD=runcmd, DEBUGMODE=debug):
            run(runcmd, warn_only=True)

    url = "http://%s:%s/static/index.html" % (host, port)
    if web:
        webbrowser.open_new_tab(url)
        msg = "Opening %s in browser"
    else:
        msg = "Monitor results at: %s"
    print(msg % url)
    time.sleep(1)

    load(concurrency, duration, host=host, port=port if not proxy else srv['proxy_port'])

