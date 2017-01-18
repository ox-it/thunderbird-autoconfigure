import socket
import dns.resolver

class UndeliverableAddress(Exception):
    pass
class UnconfigurableDomain(Exception):
    pass

class MTAConnection(object):
    INVALID_LOCALPART = 'invalid.localpart.1234567890'

    def __init__(self, hostname, port=25):
        self._hostname, self._port = hostname, port
        self._conn = None

    def __enter__(self):
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn.connect((self._hostname, self._port))
        self._get_line()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._conn.close()

    def _query(self, s):
        self._conn.send(s)
        return self._get_line()

    def _get_line(self):
        response = []
        while True:
            char = self._conn.recv(1)
            if char == '\n':
                break
            response.append(char)
        return ''.join(response)

    def is_nexus_domain(self, domain):

        # Check that this MTA is in the MX record for this domain.
        try:
            answers = dns.resolver.query(domain, 'MX')
        except dns.resolver.NXDOMAIN, e:
            return False
        if not any(answer.exchange.to_text() == (self._hostname + '.') for answer in answers):
            return False
        
        response = self._query('EXPN %s@%s\n' % (self.INVALID_LOCALPART, domain))
        if response.startswith('250 '):
            return False
        elif response.startswith('553 '):
            # The MTA knows that the address is undeliverable.
            return True

    def get_username(self, address):
        response = self._query('EXPN %s\n' % address).strip()
        if not response.startswith('250 '):
            raise UndeliverableAddress("%r is undeliverable" % address)

        # "250 <abcd0123@nexus.ox.ac.uk>"
        address = response[5:-1]
        username, domain = address.split('@')

        if domain != 'nexus.ox.ac.uk':
            raise UnconfigurableDomain("%r is not on a domain we can provide configuration for" % address)

        return username

    def close(self):
        self._conn.close()
