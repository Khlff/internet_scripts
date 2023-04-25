import argparse
import socket
import threading


class PortScanner:
    def __init__(self, host: str, port_range: set):
        self.ports = []
        self.start, self.end = port_range
        self.host = host
        self.protocols = {
            80: 'HTTP',
            123: 'SNTP',
            53: 'DNS',
            25: 'SMTP',
            110: 'POP3',
            143: 'IMAP'
        }

    def _scan_tcp_port(self, host: str, port: int) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
            protocol = self.protocols.get(port, '')
            self.ports.append(f'TCP {port} {protocol}')
        except ConnectionError:
            pass
        except PermissionError:
            print("\033[31mPermission denied\033[0m")
        finally:
            sock.close()

    def _scan_udp_port(self, host: str, port: int) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                protocol = self.protocols.get(port, '')
                if protocol:
                    self.ports.append(f'UDP {port} {protocol}')
        except PermissionError:
            print("\033[31mPermission denied\033[0m")
        except OSError:
            pass
        finally:
            sock.close()

    def check_tcp_ports(self) -> None:
        for port in range(self.start, self.end + 1):
            t = threading.Thread(target=self._scan_tcp_port,
                                 args=(self.host, port))
            t.start()

    def check_udp_ports(self) -> None:
        for port in range(self.start, self.end + 1):
            t = threading.Thread(target=self._scan_udp_port,
                                 args=(self.host, port))
            t.start()

    def get_scanned_ports(self) -> list:
        return sorted(self.ports)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action='store_true', help='Scan TCP ports')
    parser.add_argument('-u', action='store_true', help='Scan UDP ports')
    parser.add_argument('host', help='Host to scan', default='localhost')
    parser.add_argument('ports', metavar='N1 N2', type=int, nargs=2,
                        help='Port range to scan')
    args = parser.parse_args()

    port_scanner = PortScanner(args.host, args.ports)
    if args.t:
        port_scanner.check_tcp_ports()

    if args.u:
        port_scanner.check_udp_ports()

    for port in port_scanner.get_scanned_ports():
        print(port)


if __name__ == '__main__':
    main()
