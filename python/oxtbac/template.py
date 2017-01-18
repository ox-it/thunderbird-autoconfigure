"""
Contains the template response.
"""

TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<clientConfig>
  <emailProvider id="Nexus">
    <domain/>
    <displayName>University of Oxford</displayName>
    <displayShortName>Nexus</displayShortName>
    <incomingServer type="imap">
      <hostname>imap.nexus.ox.ac.uk</hostname>
      <port>143</port>
      <socketType>STARTTLS</socketType>
      <username/>
      <authentication>plain</authentication>
    </incomingServer>
    <outgoingServer type="smtp">
      <hostname>smtp.ox.ac.uk</hostname>
      <port>587</port>
      <socketType>STARTTLS</socketType>
      <username/>
      <authentication>plain</authentication>
      <addThisServer>true</addThisServer>
      <useGlobalPreferredServer>false</useGlobalPreferredServer>
    </outgoingServer>
  </emailProvider>
</clientConfig>
"""
