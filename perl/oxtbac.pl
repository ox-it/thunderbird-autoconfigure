#!/usr/bin/perl

use strict;
use CGI;
use Net::IP::CMatch;
use IO::Socket;
use String::Random qw{random_regex};
use Net::DNS qw{mx};
require XML::Generator;

my @oxfordIPRanges = qw{129.67.0.0/16
                        163.1.0.0/16
                        192.76.16.0/20
                        192.76.32.0/22
                        2001:630:440::/44};

my $relay = 'oxmail.ox.ac.uk';

use constant { NOT_NEXUS_DOMAIN => 1,
               NOT_NEXUS_ADDRESS => 2,
               UNDELIVERABLE_ADDRESS => 3,
               VALID_ADDRESS => 4 };

sub is_oxford_ip {
    return match_ip(shift, @oxfordIPRanges);
}

sub done_with_oxmail {
    my ($socket, $status, $username) = @_;
    print $socket "QUIT\n";
    $socket->close;
    return $status, $username;
}

sub handled_by_oxmail {
    my @mx = mx($_[0]);
    my $rr;
    foreach $rr (@mx) {
        return 1 if ($rr->exchange eq 'oxmail.ox.ac.uk');
    }
    return 0;
}

sub get_mailbox_params {
    my ($emailaddress, $resolve_username) = @_;

    if ($emailaddress !~ /[a-zA-Z\d\-.]+@[a-z.\-\d]+/) {
        return NOT_NEXUS_DOMAIN, '';
    }

    my ($localpart, $domain) = split(/\@/, $emailaddress);

    # Test domain to see whether the oxmails are supposed to handle mail
    # for it. If not then it can't be a Nexus domain
    return NOT_NEXUS_DOMAIN, '' if (!handled_by_oxmail($domain));

    my $random = random_regex("\\w{16}");

    my $socket = new IO::Socket::INET(PeerAddr => $relay,
                                      PeerPort => 25,
                                      Proto    => 'tcp')
                 or die "Cannot connect to the mail relay";

    $socket->autoflush(1);

    die "Server not welcoming" if (<$socket> !~ /^220 /);

    # Say hello
    print $socket "HELO autoconfig.nexus.ox.ac.uk\n";
    die "Server didn't like hello" if (<$socket> !~ /^250 /);

    # Test domain to see if it's handled by Nexus.  The relay will know when
    # addresses are non-deliverable if they are Nexus ones.
    print $socket "EXPN $random\@$domain\n";
    return done_with_oxmail($socket, NOT_NEXUS_DOMAIN, '') if (<$socket> !~ /^553 /);

    # If we shouldn't be resolving the username then stop here.
    return done_with_oxmail($socket, VALID_ADDRESS, '') if (!$resolve_username);

    print $socket "EXPN $emailaddress\n";
    my $response = <$socket>;

    return done_with_oxmail($socket, UNDELIVERABLE_ADDRESS, '') if ($response !~ /^250 /);

    $response =~ s/^250 <([\w\-.]+)@([\w\-.]+)>.*\n/$1\@$2/;
    
    my ($username, $target_domain) = split(/\@/, $response);

    if ($target_domain eq "nexus.ox.ac.uk") {
        return done_with_oxmail($socket, VALID_ADDRESS, $username);
    } else {
        return done_with_oxmail($socket, NOT_NEXUS_ADDRESS, '');
    }
}


my $q = new CGI;

my $emailaddress = lc $q->param('emailaddress') ;

my ($status, $username) = get_mailbox_params($emailaddress, is_oxford_ip($q->remote_host));

if ($status == NOT_NEXUS_DOMAIN) {
    print "Status: 404 Not Found\n";
    print "Content-type: text/plain\n\n";
    print "You haven't supplied an e-mail addres whose domain is handled by Nexus.\n";
    exit;
}

$username = "Mistyped addr.?" if ($status == UNDELIVERABLE_ADDRESS);
$username = "Not Nexus addr." if ($status == NOT_NEXUS_ADDRESS);

my $X = XML::Generator->new(pretty => '  ', empty => 'compact');

my $config = $X->clientConfig(
  $X->emailProvider({id => 'Nexus'},
    $X->domain,
    $X->displayName('University of Oxford'),
    $X->displayShortName('Nexus'),
    $X->incomingServer({type => 'imap'},
      $X->hostname('imap.nexus.ox.ac.uk'),
      $X->port(143),
      $X->socketType('STARTTLS'),
      $X->username($username),
      $X->authentication('plain'),
    ),
    $X->outgoingServer({type => 'smtp'},
      $X->hostname('smtp.ox.ac.uk'),
      $X->port(587),
      $X->socketType('STARTTLS'),
      $X->username($username),
      $X->authentication('plain'),
      $X->addThisServer('true'),
      $X->useGlobalPreferredServer('false'),
    ),
  ),
);
    
print "Status: 200 OK\n";
print "Content-type: application/xml\n\n";
print $config;
print "\n";

