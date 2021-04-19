import socket
import struct
import sys

message = 'sync'.encode()
multicast_group = ('224.64.16.1', 3956)

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout(10)

# Set the time-to-live for messages to 1 so they do not go past the
# local network segment.
ttl = struct.pack('b', 2)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

try:

    # Send data to the multicast group
    print('sending "%s"' % message)
    sent = sock.sendto(message, multicast_group)

    # Look for responses from all recipients
    while True:

        print('waiting to receive')
        try:
            data, server = sock.recvfrom(16)
        except socket.timeout:
            print('timed out, no more responses')
            break
        else:
            print('received "%s" from %s' % (data, server))
            #print >>sys.stderr, 'received "%s" from %s' % (data, server)



finally:

    print( 'closing socket')
    sock.close()