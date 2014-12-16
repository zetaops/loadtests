__author__ = 'Evren Esat Ozkan'
# import os
# import sys
# import site
#site.addsitedir("/Library/Python/2.7/site-packages")


# from pycounters import shortcuts, reporters, start_auto_reporting, register_reporter
# import logging
# from pycounters.shortcuts import frequency

# JSONFile = "./server.counters.json"
#
# reporter = reporters.JSONFileReporter(output_file=JSONFile)
# register_reporter(reporter)
# reporter=reporters.LogReporter(logging.getLogger("mylog"))
# register_reporter(reporter)

# start_auto_reporting(3)

# from gevent import monkey
# monkey.patch_all()


# @frequency()
def application(environ, start_response):
    status = '200 OK'
    output = 'Pong!'

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]

