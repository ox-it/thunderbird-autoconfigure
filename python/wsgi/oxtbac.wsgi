import os, sys, os.path

sys.path.insert(0, os.path.dirname(__file__))

import server
from template import TEMPLATE

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
