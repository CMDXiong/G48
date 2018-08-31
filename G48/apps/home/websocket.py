# -*- coding: utf-8 -*-

import threading
import hashlib
import socket
import base64
import views
from views import fuzzy_query_test, update_svn, send_msg1
import time
import os
import json

global_data1 = {}
update_config = {}


class websocket_thread(threading.Thread):
    def __init__(self, connection):
        super(websocket_thread, self).__init__()
        self.connection = connection

    def run(self):
        print 'new websocket client joined!'

        while True:
            data = self.connection.recv(1024)
            if data:
                real_data = parse_data(data)
                if real_data:
                    try:
                        query_info_dict = json.loads(real_data)
                    except ValueError:
                        print "ValueError"
                    if query_info_dict.has_key('type'):
                        if query_info_dict["type"] == "svnUpdate":           # svn配置更新
                            global update_config
                            update_config = query_info_dict
                            local_road = query_info_dict['localRoad']
                            if not os.path.exists(local_road):                # 路径有问题
                                update_info = {"type": "path_error"}
                                send_msg1(self.connection, update_info)
                            else:
                                update_info = {"type": "svn_config_success"}
                                send_msg1(self.connection, update_info)
                        elif query_info_dict["type"] == "update_request":  # 数据更新请求
                            start1 = time.clock()
                            # update_svn(update_config)
                            end1 = time.clock()
                            print "svn下拉时间: ", end1 - start1
                            # local_road = ur'F:\Project\错误的文件'
                            local_road = update_config['localRoad']
                            files_num = sum([len(x) for _, _, x in os.walk(local_road)])
                            # files_num = 1
                            global global_data1
                            start2 = time.clock()
                            global_data1 = views.datas_form_files_test(local_road, files_num, self.connection)
                            send_msg1(self.connection, {"type": "load_data_finish"})
                            end2 = time.clock()
                            print "数据载入内存时间: ", end2 - start2
                        elif query_info_dict["type"] == "queryInfo":
                            start = time.clock()
                            fuzzy_query_test(global_data1, self.connection, query_info_dict)
                            end = time.clock()
                            print "查询时间：", start - end
                        else:
                            pass
            break


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


def init_server_websocket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # sock.bind(('127.0.0.1', 9005))
    # sock.bind(('10.240.113.164', 9005))
    sock.bind(('0.0.0.0', 9005))
    sock.listen(100)
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
