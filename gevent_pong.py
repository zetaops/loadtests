__author__ = 'Evren Esat Ozkan'

from gevent import wsgi
from pong import application

from gevent import monkey
monkey.patch_all()

wsgi.WSGIServer(('', 8088), application).serve_forever()
