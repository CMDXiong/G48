# -*- coding: utf-8 -*-

import threading
import hashlib
import socket
import base64
import views
from views import fuzzy_query

global global_data1
global_data1 = {}
global files_counts
files_counts = 0


class websocket_thread(threading.Thread):
    def __init__(self, connection):
        super(websocket_thread, self).__init__()
        self.connection = connection

    def run(self):
        print 'new websocket client joined!'
        reply = 'i got u, from websocket server 2222'
        # length = len(reply)
        while True:
            data = self.connection.recv(1024)
            if data is not None:
                re = parse_data(data)
                print re
            print 'new test'

            fuzzy_query(u"击杀间隔", global_data1, self.connection, files_counts)


def parse_data(msg):
    v = ord(msg[1]) & 0x7f
    if v == 0x7e:
        p = 4
    elif v == 0x7f:
        p = 10
    else:
        p = 2
    mask = msg[p:p + 4]
    data = msg[p + 4:]

    return ''.join([chr(ord(v) ^ ord(mask[k % 4])) for k, v in enumerate(data)])


def parse_headers(msg):
    headers = {}
    header, data = msg.split('\r\n\r\n', 1)
    for line in header.split('\r\n')[1:]:
        key, value = line.split(': ', 1)
        headers[key] = value
    headers['data'] = data
    return headers


def generate_token(msg):
    key = msg + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    ser_key = hashlib.sha1(key).digest()
    return base64.b64encode(ser_key)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', 9005))
    sock.listen(5)

    # 初始化数据
    # filepath = ur'F:\Project\H37\H37_xls_search\05Data\pvp数据表'
    # filepath = ur'F:\Project\H37\H37_xls_search\05Data'
    filepath = ur'F:\Project\H37\H37_xls_search\test_file'

    files_counts, global_data1 = views.datas_form_files(filepath)
    print files_counts

    while True:
        connection, address = sock.accept()
        try:
            data = connection.recv(1024)
            headers = parse_headers(data)
            token = generate_token(headers['Sec-WebSocket-Key'])
            connection.send('\
HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n' % token)
            thread = websocket_thread(connection)
            thread.start()
        except socket.timeout:
            print 'websocket connection timeout'
