#!/usr/bin/env python

import os, sys

from oxtbac import server
from oxtbac.template import TEMPLATE

RELAY = 'oxmail.ox.ac.uk'
NETMASKS = [
    '0.0.0.0/0',
    '129.67.0.0/16',
    '163.1.0.0/16',
    '192.76.16.0/20',
    '192.76.32.0/22',
    '2001:630:440::/44',
]

application = server.AutoConfigHandler(RELAY, NETMASKS, TEMPLATE)

def start_response(code, headers):
    print "Status: %s" % code
    for header in headers:
        print "%s: %s" % header
    print

if __name__ == '__main__':
    environ = os.environ.copy()
    environ.update({
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https' if environ.get('HTTPS') else 'http',
        'wsgi.input': sys.stdin,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': True,
    })

    for line in application(environ, start_response):
         print line
