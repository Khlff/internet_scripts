# import argparse
# import socket
# import struct
# import sys
# import threading
# from time import time, sleep
# from concurrent.futures import ThreadPoolExecutor
#
# NTP_EPOCH = 2208988800  # 1900-01-01 00:00:00
#
#
# def get_current_time(delay):
#     t = time() + delay + NTP_EPOCH
#     seconds, fraction = int(t), int((t - int(t)) * 2 ** 32)
#     return seconds, fraction
#
#
# def handle_client(client_address, delay):
#     print(f"Connected: {client_address}")
#     seconds, fraction = get_current_time(delay)
#     packet = struct.pack('!BBBb11I2I',
#                          (2 << 6) | (4 << 3) | 4,  # LI, VN, Mode
#                          1,  # Stratum
#                          0,  # Poll Interval
#                          0,  # Precision
#                          0, 0, 0, 0, 0, 0, 0, 0,
#                          # Root Delay, Root Dispersion, Ref ID
#                          seconds,  # Reference Timestamp (seconds)
#                          fraction,  # Reference Timestamp (fraction)
#                          seconds,  # Originate Timestamp (seconds)
#                          fraction,  # Originate Timestamp (fraction)
#                          seconds,  # Receive Timestamp (seconds)
#                          fraction,  # Receive Timestamp (fraction)
#                          seconds,  # Transmit Timestamp (seconds)
#                          fraction)  # Transmit Timestamp (fraction)
#
#     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
#         sock.sendto(packet, client_address)
#
#
# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-d', '--delay', type=int, default=0,
#                         help='Delay in seconds')
#     parser.add_argument('-p', '--port', type=int, default=123,
#                         help='Port to listen on')
#     args = parser.parse_args()
#
#     print(f"Server started with delay {args.delay} on port {args.port}")
#
#     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
#         server_socket.bind(('', args.port))
#         server_socket.settimeout(1)
#
#         with ThreadPoolExecutor(max_workers=10) as executor:
#             while True:
#                 try:
#                     data, addr = server_socket.recvfrom(1024)
#                     if data:
#                         executor.submit(handle_client, addr, args.delay)
#                 except socket.timeout:
#                     pass
#
#
# if __name__ == '__main__':
#     main()
import socket
import struct
import time

# Серверный адрес и порт
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 123

# Часовой пояс, используемый для вычисления корректного времени
TIME_ZONE = 3 * 3600  # Вы должны установить свой собственный часовой пояс

# NTP-пакет состоит из 48 байт, первые 32 из которых - это секунды, начиная с 1 января 1900 года
# Оставшиеся 16 байт - это дробная часть секунды, представленная в виде 32-битного целого числа
NTP_PACKET_FORMAT = "!12I"


def get_ntp_time():
    # NTP-пакет содержит 12 байт заголовка, начиная с поля LI, VN, Mode
    # Нам нужно только указать, что мы хотим получить NTP-время (Mode = 3)
    ntp_packet = struct.pack(NTP_PACKET_FORMAT,
                             0x1B,  # LI, VN, Mode
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    # Создаем сокет и отправляем NTP-запрос на сервер
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(ntp_packet, (SERVER_ADDRESS, SERVER_PORT))
    # Получаем ответ от сервера и извлекаем NTP-время из пакета
    data, server = client_socket.recvfrom(1024)
    ntp_time = struct.unpack(NTP_PACKET_FORMAT, data)[10]
    ntp_time -= TIME_ZONE  # Вычитаем часовой пояс для получения корректного времени
    return ntp_time


def ntp_server():
    # Создаем сокет и привязываем его к серверному адресу и порту
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
    print(f"Server started on {SERVER_ADDRESS}:{SERVER_PORT}")
    # Бесконечный цикл для обработки входящих запросов
    while True:
        data, client_address = server_socket.recvfrom(1024)
        print(f"Received request from {client_address}")
        # Получаем текущее NTP-время и формируем NTP-ответ
        ntp_time = int((time.time() + TIME_ZONE) * (2 ** 32 / 1e6))
        ntp_packet = struct.pack(NTP_PACKET_FORMAT,
                                 0x1C,  # LI, VN, Mode
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 ntp_time)
        # Отправляем NTP-ответ обратно клиенту
        server_socket.sendto(ntp_packet, client_address)


if __name__ == '__main__':
    ntp_server()
