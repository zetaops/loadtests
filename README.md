# WSGI Webserver Loadtesting Thingy

This project aims to ease the testing of WSGI web servers with the help of a few Fabric tasks.
It has a realtime load visulation for RPS, CPU and Memory usage of web server.

We used PyCounters to count and display the requests per second. Unfortunately we realized that, PyCounters is not not
working with async cores (gevent) So we added support for the both web server's own stat sharing protocols. (a client for uwsgi and an udp server for the gunicorn)

We used psutil to collect the memory and cpu usage of the web server process.


Web interface and command line options can be seen below;


➤ fab -l
Available commands:

    error  Call ``func`` with given error ``message``.
    kill   first we politely ask to stop, then throw a  SIGKILL signal, just in case...
    load   this will stress the server via wrk load testing tool.
    sync   syncs the files with test machine (to home dir. by default)
    test   deploy files, run the selected wsgi server and start load testing.


➤ fab -d test
Displaying detailed information for task 'test':

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

    Arguments: server='gunicorn', host='148.251.192.21', port='8000', gevent='', concurrency='50', workers='', threads='', debug='', nohup='', web='', duration='40', count='', proxy='', xtra=''
