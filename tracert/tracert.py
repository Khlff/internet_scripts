import ipaddress
import re
import sys
from logging import warning
from socket import socket, AF_INET, SOCK_RAW, IPPROTO_ICMP, \
    IPPROTO_IP, IP_HDRINCL, error, SOCK_DGRAM, create_connection, \
    timeout, gethostbyname, gaierror
from struct import pack

import arg_parser

DEFAULT_TTL = 30
DEFAULT_WHOIS_SERVER = "whois.iana.org"
WHOIS_PORT = 43
TIMEOUT = 5


def main():
    destination = arg_parser.arg_parse()

    try:
        sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
        sock.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
        sock.settimeout(TIMEOUT)
    except error:
        print("Permission denied")
        sys.exit(0)

    source = get_ip()
    try:
        try:
            address = gethostbyname(destination[0])
            print(address + ":")
            hope = 1
            current_address = ""
            max_ttl = DEFAULT_TTL
            while hope <= max_ttl and current_address != address:
                buff = package_assembly(hope, source, address)
                sock.sendto(buff, (destination[0], 0))
                try:
                    reply = sock.recvfrom(1024)
                    current_address = reply[1][0]
                    print(f"{hope}) {current_address}")
                    if is_local_ip(current_address):
                        print("local")
                    country, netname, autonomic_system = get_info(current_address)
                    if country is not None:
                        print(f"\tCountry: {country}")
                    if netname is not None:
                        print(f"\tNetname: {netname}")
                    if autonomic_system is not None:
                        print(f"\tAutonomic system: {autonomic_system}")
                    print()
                except timeout:
                    print(f"{hope}) {'*'}")
                    print()
                hope += 1
        except gaierror:
            warning(f"Wrong destination: {destination[0]}")
    except timeout:
        print("Timeout exceeded.")
    finally:
        sock.close()


def is_local_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return ip_obj.is_private


def package_assembly(ttl, source, destination):
    version_ihl = 4 << 4 | 5
    total_length = 60
    protocol_icmp = 1
    source = address_format(source)
    destination = address_format(destination)
    echo_icmp = 8

    ip_header = pack("!BBHLBBH", version_ihl, 0, total_length,
                     0, ttl, protocol_icmp, 0) + source + destination
    icmp_header = pack("!BBHL", echo_icmp, 0, 0, 0)
    icmp_checksum = calc_checksum(icmp_header)
    icmp_header = pack("!BBHL", echo_icmp, 0, icmp_checksum, 0)
    result = ip_header + icmp_header

    return result


def address_format(address):
    addr = tuple(int(x) for x in address.split('.'))
    return pack("!BBBB", addr[0], addr[1], addr[2], addr[3])


def get_ip():
    sock = socket(AF_INET, SOCK_DGRAM)
    try:
        sock.connect((DEFAULT_WHOIS_SERVER, WHOIS_PORT))
        return sock.getsockname()[0]
    finally:
        sock.close()


def calc_checksum(packet):
    words = [int.from_bytes(packet[_:_ + 2], "big") for _ in range(0, len(packet), 2)]
    checksum = sum(words)
    while checksum > 0xffff:
        checksum = (checksum & 0xffff) + (checksum >> 16)
    return 0xffff - checksum


def send_request(request, host_port):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    sock = create_connection(host_port, TIMEOUT)
    data = bytes()
    try:
        sock.sendall(f"{request}\r\n".encode('utf-8'))
        while True:
            buff = sock.recv(1024)
            if not buff:
                return data.decode("utf-8")
            data += buff
    finally:
        sock.close()


def get_info(address):
    refer = re.compile(r"refer: (.*?)\n")
    country = re.compile(r"country: (.*?)\n")
    netname = re.compile(r"netname: (.*?)\n")
    autonomic_system = re.compile(r"origin: (.*?)\n")
    reply = send_request(address, (DEFAULT_WHOIS_SERVER, WHOIS_PORT))
    refer = re.search(refer, reply)
    if refer is not None:
        refer = refer.groups()[0].replace(' ', '')
        reply = send_request(address, (refer, WHOIS_PORT))
    for pattern in country, netname, autonomic_system:
        match = re.search(pattern, reply)
        if match is not None:
            yield match.groups()[0].replace(' ', '')
        else:
            yield None


if __name__ == "__main__":
    main()
