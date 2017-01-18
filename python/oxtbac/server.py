
import urlparse
import re
from xml.etree import ElementTree as etree
from IPy import IP

from mta import MTAConnection, UndeliverableAddress, UnconfigurableDomain

class AutoConfigHandler(object):
    _EMAIL_RE = re.compile(r'[a-zA-Z\d\-.]+@[a-z.\-\d]+')

    def __init__(self, relay, netmasks, template):
        self._relay, self._netmasks, self._template = relay, map(IP, netmasks), template

    def __call__(self, environ, start_response):
        script_name, path_info = environ.get('SCRIPT_NAME', ''), environ.get('PATH_INFO', '')
        if (script_name and path_info) or (not script_name and path_info != '/'):
            return self._handle_404(environ, start_response, 'Not found')

        query_string = urlparse.parse_qs(environ.get('QUERY_STRING', ''))
        email_address = query_string.get('emailaddress', [''])[0]
        if not self._EMAIL_RE.match(email_address):
            return self._handle_404(environ, start_response, 'Invalid e-mail address.')

        domain = email_address.split('@')[-1]

        username = ''

        with MTAConnection(self._relay) as conn:
            if not conn.is_nexus_domain(domain):
                return self._handle_404(environ, start_response, 'Unknown domain.')

            if self.is_university_host(environ['REMOTE_ADDR']):
                try:
                    username = conn.get_username(email_address)
                except UndeliverableAddress:
                    username = 'Mistyped email addr.?'
                except UnconfigurableDomain:
                    username = 'Not a Nexus mailbox.'
                username = u'\u1234'

        template = etree.fromstring(self._template)
        for elem in template.findall('.//username'):
            elem.text = username
        for elem in template.findall('.//domain'):
            elem.text = domain

        start_response('200 OK',
                       #[('Content-Type', 'application/xml')])
                       [('Content-Type', 'text/plain')])

        return [etree.tostring(template, encoding='utf-8')]

    def is_university_host(self, ip):
        return any((ip in netmask) for netmask in self._netmasks)
        
    def _handle_404(self, environ, start_response, message):
        start_response('404 Not Found',
                       [('Content-Type', 'text/plain')])
        return [message]

