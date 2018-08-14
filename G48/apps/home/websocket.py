# -*- coding: utf-8 -*-

import threading
import hashlib
import socket
import base64
import views
from views import fuzzy_query_test, update_svn, send_msg
import time
import os

global_data1 = {}


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
                print "real_data", real_data
                if real_data:
                    import json
                    query_info_dict = json.loads(real_data)
                    print query_info_dict
                    if query_info_dict.has_key('type'):
                        if query_info_dict["type"] == "svnUpdate":
                            name = query_info_dict['name']
                            host = query_info_dict['host']
                            username = query_info_dict['username']
                            password = query_info_dict['password']
                            local_road = query_info_dict['localRoad']
                            # update_svn(query_info_dict)
                            local_road = ur'F:\Project\错误的文件'
                            files_num = sum([len(x) for _, _, x in os.walk(local_road)])
                            global global_data1
                            global_data1 = views.datas_form_files_test(local_road, files_num, self.connection)
                            # if "badFiles" in global_data1:
                            #     if global_data1["badFiles"]:
                            #         content = {"type": "badFiles", "badFiles": global_data1["badFiles"]}
                            #
                            #         print "global_data1", global_data1["badFiles"]
                            #         json_str = json.dumps(content)
                            #         send_msg(self.connection, json_str)

                            time.sleep(5)
                            context = {"type": "finish_data_update"}
                            json_str = json.dumps(context)
                            send_msg(self.connection, json_str)
                            print "完成"
                        elif query_info_dict["type"] == "queryInfo":
                            start = time.clock()
                            # data1 = {}
                            # data2 = {}
                            # for key, value in global_data1.items():
                            #     len_list = len(value)
                            #     if len_list >= 1:
                            #         data1[key] = value[0:len_list / 2]
                            #         data2[key] = value[len_list / 2:]  # 不+1，愕然为空
                            #     else:
                            #         data1[key] = []
                            #         data2[key] = []
                            #
                            fuzzy_query_test(global_data1, self.connection, query_info_dict)
                            end = time.clock()
                            print "查询时间：", start - end
                    else:
                        pass


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
    sock.listen(5)

    # 初始化数据
    # filepath = ur'F:\Project\H37\H37_xls_search\03SystemSetting\04单位系统\BOSS缩放表.xlsx'
    # filepath = ur'F:\Project\H37\H37_xls_search\05Data'
    # filepath = ur'F:\Project\H37\H37_xls_search\test_file'
    # filepath = ur'F:\Project\H37\H37_xls_search'
    # filepath = ur'F:\Project\G48\导表3'
    # filepath = ur'F:\Project\G48\导表3\01贸易数值表.xls'
    # filepath = ur'F:\Project\test'
    # filepath = ur'F:\Project\数据表'
    # filepath = ur'F:\Project\福哥'
    filepath = ur'F:\Project\错误的文件'

    start = time.clock()
    global global_data1
    # global_data1 = views.datas_form_files_test(filepath)
    end = time.clock()
    print "数据载入完成, 载入数据时间：", start - end

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


# if __name__ == '__main__':
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     # sock.bind(('127.0.0.1', 9005))
#     sock.bind(('10.240.113.164', 9005))
#     # sock.bind(('0.0.0.0', 9005))
#     sock.listen(5)
#
#     # 初始化数据
#     # filepath = ur'F:\Project\H37\H37_xls_search\03SystemSetting\04单位系统\BOSS缩放表.xlsx'
#     # filepath = ur'F:\Project\H37\H37_xls_search\05Data'
#     # filepath = ur'F:\Project\H37\H37_xls_search\test_file'
#     # filepath = ur'F:\Project\H37\H37_xls_search'
#     # filepath = ur'F:\Project\G48\导表3'
#     # filepath = ur'F:\Project\G48\导表3\01贸易数值表.xls'
#     filepath = ur'F:\Project\test'
#     # filepath = ur'F:\Project\数据表'
#
#
#     import time
#     start = time.clock()
#     global global_data1
#     global_data1 = views.datas_form_files_test(filepath)
#     end = time.clock()
#     print "数据载入完成, 载入数据时间：", start - end
#
#     while True:
#         connection, address = sock.accept()
#         try:
#             data = connection.recv(1024)
#             headers = parse_headers(data)
#             token = generate_token(headers['Sec-WebSocket-Key'])
#             connection.send('\
# HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
# Upgrade: WebSocket\r\n\
# Connection: Upgrade\r\n\
# Sec-WebSocket-Accept: %s\r\n\r\n' % token)
#             thread = websocket_thread(connection)
#             thread.start()
#         except socket.timeout:
#             print 'websocket connection timeout'
