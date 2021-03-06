# WSGI Webserver Load Testing Suite

This project aims to ease the testing of Python WSGI web servers (gunicorn and uWSGI for now) with the help of a few fabric tasks.
Addition to utility fabric tasks, it shows realtime load visulation for RPS, CPU and Memory usage of web server.

![](https://raw.githubusercontent.com/zetaops/loadtests/master/docs/webui1.png)

At first, we implement PyCounters to gather the requests per second data. But later we realized that, PyCounters isn't
working with async cores (gevent). So we added support for the both web server's own stat sharing protocols. (a client for uwsgi and an udp server for the gunicorn)
For non-async workers, pycounters can be enabled with __count__ parameter. 

psutil used to collect the memory and cpu usage of the web server process.


## Dependencies
#### (for a Debian based distro)
    apt-get install libssl-dev nginx build-essential python-dev  python-pip git
    pip install flask psutil
    git clone https://github.com/wg/wrk.git; cd wrk; make ; sudo cp wrk /usr/local/bin


## Installation & Usage
Create a __local_settings.py__ file with the following contents.
```python
    HOST = ''
    PORT = "22"
    WORKING_DIR = ''
    USER = ''
```

Command line options can be seen below;


➤ fab -l

    kill   first we politely ask to stop, then throw a  SIGKILL signal, just in case...
    load   this will stress the server via wrk load testing tool.
    sync   syncs the files with test machine (to home directory by default)
    test   deploy files, run the selected wsgi server and start load testing.


Displaying detailed information for task 'test'


➤ fab -d test

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

    Arguments: server='gunicorn', host='localhost', port='8000', gevent='', concurrency='50', workers='', threads='', debug='', nohup='', web='', duration='40', count='', proxy='', xtra=''


Tests can be run like this: 

    fab test:gunicorn,duration=10
    fab test:gunicorn,workers=10,web=1
    fab kill:gunicorn
    fab test:uwsgi,concurrency=200,count=1,duration=40
    fab load:200


Note: If you want to test the "behind nginx" performance, you should configure nginx with the config files stored within ngnix directory
