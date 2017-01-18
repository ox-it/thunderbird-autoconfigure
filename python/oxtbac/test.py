from wsgiref.simple_server import make_server

from server import AutoConfigHandler
from template import TEMPLATE

RELAY = 'oxmail.ox.ac.uk'
NETMASKS = ['0.0.0.0/0']

if __name__ == '__main__':
    handler = AutoConfigHandler(RELAY, NETMASKS, TEMPLATE)
    httpd = make_server('', 8000, handler)
    httpd.serve_forever()
