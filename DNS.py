import socket
import struct
import random

# Function to build a DNS query
def build_query(domain):
    ID = random.randint(0, 65535)
    FLAGS = 0x0100  # Standard query with recursion
    QDCOUNT = 1     # Number of questions
    ANCOUNT = 0     # Number of answers
    NSCOUNT = 0     # Number of authority records
    ARCOUNT = 0     # Number of additional records
    query_type = 1  # Type A query (Host address)
    query_class = 1 # Class IN (Internet)

    header = struct.pack('>HHHHHH', ID, FLAGS, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)
    question = b''.join([struct.pack('>B', len(label)) + label.encode() for label in domain.split('.')]) + b'\x00'
    question += struct.pack('>HH', query_type, query_class)

    return header + question

# Function to send DNS query
def send_query(query, server='8.8.8.8', port=53):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(query, (server, port))
        response, _ = s.recvfrom(512)
    return response

# Function to parse a single resource record
def parse_rr_section(section, offset):
    if section[offset] & 0xC0 == 0xC0:
        pointer = struct.unpack('>H', section[offset:offset+2])[0] & 0x3FFF
        offset += 2
        name = None
    else:
        name = []
        while section[offset] != 0:
            length = section[offset]
            offset += 1
            name.append(section[offset:offset+length].decode())
            offset += length
        offset += 1
        name = '.'.join(name)

    rrtype, rrclass, ttl, rdlength = struct.unpack('>HHIH', section[offset:offset+10])
    rdata = section[offset+10:offset+10+rdlength]
    offset += 10 + rdlength

    return name, rrtype, rrclass, ttl, rdata, offset

# Function to resolve a DNS query
def resolve_dns(domain, server='198.41.0.4', port=53):
    query = build_query(domain)
    response = send_query(query, server, port)

    header = response[:12]
    ID, flags, qdcount, ancount, nscount, arcount = struct.unpack('>HHHHHH', header)
    offset = 12

    for _ in range(qdcount):
        while response[offset] != 0:
            offset += 1
        offset += 5

    a_records = []
    for _ in range(ancount):
        name, rrtype, _, _, rdata, new_offset = parse_rr_section(response, offset)
        if rrtype == 1:
            ip_address = socket.inet_ntoa(rdata)
            a_records.append(ip_address)
        offset = new_offset

    if a_records:
        return a_records

    ns_records = []
    for _ in range(nscount):
        name, rrtype, _, _, rdata, new_offset = parse_rr_section(response, offset)
        if rrtype == 2:
            ns_records.append(name)
        offset = new_offset

    for _ in range(arcount):
        name, rrtype, _, _, rdata, new_offset = parse_rr_section(response, offset)
        if rrtype == 1 and name in ns_records:
            ip_address = socket.inet_ntoa(rdata)
            return resolve_dns(domain, ip_address)
        offset = new_offset

    for ns in ns_records:
        return resolve_dns(domain, ns)

    return None

# Main function to test the resolver
if __name__ == "__main__":
    domain_to_resolve = 'dns.google.com'
    resolved_ips = resolve_dns(domain_to_resolve)
    if resolved_ips:
        for ip in resolved_ips:
            print(f'Resolved IP for {domain_to_resolve}: {ip}')
    else:
        print(f'Could not resolve {domain_to_resolve}')