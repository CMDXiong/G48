# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from utils import restful
from openpyxl.utils import get_column_letter
import json

# 一般我是这样去设计json格式的
# {"code": 200, "message": "", "data": {}, }


import xlrd
import time
import os
import re

import pysvn
import ConfigParser

import reader


def search_result(request):
    # 搜索结果函数
    keyword = request.POST['content']                   # 获取关键字
    keyword = keyword.replace(' ', '')                  # 去掉关键字中的所有空格
    inquiry_mode = request.POST['inquiry_mode']         # 获取查询方式
    filename = request.POST['filename']                 #
    print filename
    # print request.POST['tableType']
    context = {}                                        # 传入到html模板中的数据
    print keyword
    print inquiry_mode

    if cmp(inquiry_mode, '1') == 0:                      # 模糊查询
        print '1'
    elif cmp(inquiry_mode, '2') == 0:                    # 精确查询
        print '2'
    elif cmp(inquiry_mode, '3') == 0:                    # 高级查询
        print '3'
        keyword1 = u'商会'.replace(' ', '')
        keyword2 = u'队伍'.replace(' ', '')
        context = advanced_search(keyword1, keyword2)  # 高级查询，可以同时查询多个关键字
    else:
        print "4"
    return render(request, 'home/index.html', context=context)


def index(request):
    context = {}
    return render(request, 'home/index.html', context=context)


def datas_form_files_test(file_path, files_num, connect):
    files = 0  # 已读文件个数
    content = {"type": "update_files", "finish_precent": "0%", "filename": ""}
    datas = {"xlsx": [], "xls": [], "csv": [], "badFiles": []}           # 每一个元素都是一个表的字典
    if os.path.isfile(file_path):                                        # 如果是文件
        bad_file_name = ""
        file_name = os.path.basename(file_path)                          # 得到一个路径下的文件名
        name, ext = os.path.splitext(file_path)                          # ext为文件的扩展名
        if ext == '.xlsx':                                               # 是.xlsx文件
            xlsx_data = reader.read_file_xlsx(file_path)
            if xlsx_data:
                if xlsx_data["badFile"]:
                    datas["badFiles"].append(xlsx_data["badFile"])
                    bad_file_name = xlsx_data["badFile"]
                else:
                    datas["xlsx"].append(xlsx_data)
        elif ext == '.xls':                                              # 是.xls文件
            xls_result = reader.read_file_xls(file_path)
            if xls_result:
                datas["xls"].append(xls_result)
        elif ext == '.csv':                                              # 是.xlsx文件
            csv_result = reader.read_file_csv(file_path)
            if csv_result:
                datas["csv"].append(csv_result)
        else:                                                # 不属于.xlsx，.xls，.csv文件格式
            print "文件格式不在.xlsx，.xls, .csv之中"
        files += 1
        content["filename"] = bad_file_name
        content["finish_precent"] = str(round((float(files) / files_num), 3) * 100) + '%'
        send_msg1(connect, content)
    elif os.path.isdir(file_path):  # 如果是路径
        g = os.walk(file_path)
        # path 一个目录
        # d:代表path目录所有的目录(只包含名字，不包含前面的路径)
        # filelist: 代表path目录所有的文件(也只包含名字)
        for path, dir_list, file_name_list in g:
            for file_name in file_name_list:
                bad_file_name = ""
                complete_file_name = os.path.join(path, file_name)  # 文件的完整路径名
                if os.path.splitext(file_name)[1] == '.xlsx':  # 是.xlsx文件
                    xlsx_data = reader.read_file_xlsx(complete_file_name)
                    if xlsx_data:
                        if xlsx_data["badFile"]:
                            datas["badFiles"].append(xlsx_data["badFile"])
                            bad_file_name = xlsx_data["badFile"]
                        else:
                            datas["xlsx"].append(xlsx_data)
                elif os.path.splitext(file_name)[1] == '.xls':  # 是.xls文件
                    xls_result = reader.read_file_xls(complete_file_name)
                    if xls_result:
                        datas["xls"].append(xls_result)
                elif os.path.splitext(file_name)[1] == '.csv':  # 是.csv文件
                    csv_result = reader.read_file_csv(complete_file_name)
                    if csv_result:
                        datas["csv"].append(csv_result)
                else:
                    print "文件格式不在.xlsx .xls, .cvs之中"
                files += 1
                content["filename"] = bad_file_name
                content["finish_precent"] = str(round((float(files) / files_num), 3) * 100) + '%'
                send_msg1(connect, content)
    else:
        print "找不到文件或路径"
    return datas


# 为keyword关键字的模糊查询建立查询模式。
# 例如"潘雄"，最后建立的模式为：
# ur'[\s\w|\u4e00-\u9fa5|，。；？！]*?潘[\s\w|\u4e00-\u9fa5|，。；？！]*?雄[\s\w|\u4e00-\u9fa5|，。；？！]*?'
def building_regular_expressions(keyword, query_mode):
    if not isinstance(keyword, (str, unicode, int, float, long)):
        raise TypeError('bad operand type')
    # 1: 模糊查找; 2:精确查找; 其余保留
    keyword = keyword.replace(' ', '')
    if query_mode == '1':
        insert_pattern = u'([\s\w|\u4e00-\u9fa5|，。；;,.:？！]*?)'  # 非贪婪匹配 基本汉字的unicode编码是4E00-9FA5
        pattern = insert_pattern
        last_pattern = u'([\s\w|\u4e00-\u9fa5|，。；;,.:？！]*)'
        for i in range(len(keyword)):
            if i != len(keyword) - 1:
                pattern += (u'(' + keyword[i] + u')' + insert_pattern)
            else:
                pattern += (u'(' + keyword[i] + u')' + last_pattern)
        re_pattern = re.compile(pattern)
        return re_pattern
    elif query_mode == '2':
        print "query_mode",query_mode
        pattern = u'(^' +keyword + u'$)'
        re_pattern = re.compile(pattern)
        return re_pattern
    else:
        pass


def fuzzy_query_test(datas, connection, query_info):
    if not datas:
        print "原始数据为空，请检查数据是否导入"
        return

    # 关键字的处理
    keyword = query_info["keyword"]
    query_mode = query_info["queryMode"]
    pattern = building_regular_expressions(keyword, query_mode)  # 生成关键字查询模式
    files_queried = 0  # 已查文件个数
    files_counts = 0  # 查询的总数
    not_found = True

    # 查表类型的处理
    query_table_type = query_info["tableType"]
    # 默认情况是查所有类型的表
    if not query_table_type:
        query_table_type = ['xls', 'xlsx', 'csv']

    # 计算所需要查找文件的总数
    for mode in ['xls', 'xlsx', 'csv']:
        if mode in query_table_type:
            files_counts += len(datas[mode])

    print "files_counts = ", files_counts
    if files_counts == 0:
        context = {'type': 'not_found'}
        send_msg1(connection, context)
        return

    # 查询结果
    res = {'datas': []}
    # 1:模糊查询；2:精确查询; 3: 高级查询；其于保留
    if query_info['queryMode'] in ['1', '2']:
        for mode in ['xls', 'xlsx', 'csv']:
            if mode in query_table_type:
                for xls in datas[mode]:
                    files_queried += 1
                    result = str(round((float(files_queried) / files_counts), 3) * 100)
                    length = len(result)
                    connection.send('%c%c%s' % (0x81, length, result))

                    xls_data = xls['sheets']
                    context = {'datas': []}  # 用于存储所有表的相关数据信息
                    table_info = {'row_datas': []}  # 用于存储存在关键字的行数据
                    for sheet_name, sheet_data in xls_data.items():
                        sheet_exist = False  # 某一个sheet中是否匹配了关键字
                        cols = sheet_data['cols']  # sheet对应的列数
                        row_num = -1
                        for row in sheet_data['content']:
                            row_num += 1
                            row_exist = False  # 某一行是否匹配了关键字
                            # keyword_position = {}  # 关键字位置，与对应的值
                            # is_match = map(pattern.match, row)
                            # if any(is_match):
                            #     sheet_exist = True       # 该sheet中是否匹配了关键字
                            #     keyword_position = [i for i, v in enumerate(is_match) if v]       # 匹配关键字的位置
                            #     row_data = [row_num + 1] + row
                            #     for i in keyword_position:
                            #         row_data[i+1] = deal_tuple(is_match[i].groups(), query_mode)  # 将匹配的关键字添加相应的html标签,以显示红色
                            #     table_info['row_datas'].append(row_data)                          # 将本行数据添加至存在关键字行列表中

                            col = -1
                            row_data = [row_num + 1] + row
                            for item in row:
                                col += 1
                                if not item:
                                    continue
                                is_match = pattern.match(item)  # 匹配结果
                                if is_match:  # 如果存在匹配， 则记录该行的所有数据和相关信息
                                    sheet_exist = True  # 该sheet中是否匹配了关键字
                                    row_exist = True  # 该行存在关键字的匹配
                                    row_data[col+1] = deal_tuple(is_match.groups(), query_mode)  # 将关键字标红的数据替换原来的数据
                            if row_exist:
                                table_info['row_datas'].append(row_data)  # 将本行数据添加至存在关键字行列表中
                        if sheet_exist:
                            table_info['head'] = ['行号'] + sheet_data['header']  # 存储表头信息
                            table_info['colarray'] = [''] + num_converted_into_letters(cols) # 列标签'',  '', '', 'A', 'B', 'C'...
                            table_info['table_name'] = xls['tname']  # 关键字存在的表名
                            table_info['sheet_name'] = sheet_name  # 关键字存在的sheet名
                            context['datas'].append(table_info)  # 将存在关键字的表的相关信息存储
                    if context['datas']:
                        not_found = False
                        json_str = json.dumps(context)
                        send_msg(connection, json_str)
                        res['datas'] += context['datas']
        if not_found:
            context['type'] = 'not_found'
            send_msg1(connection, context)
        return res
    elif query_info['queryMode'] == '3':
        for mode in ['xls', 'xlsx', 'csv']:
            if mode in query_table_type:
                for xls in datas[mode]:
                    files_queried += 1
                    result = str(round((float(files_queried) / files_counts), 3) * 100)
                    length = len(result)
                    connection.send('%c%c%s' % (0x81, length, result))

                    xls_data = xls['sheets']
                    context = {'datas': []}  # 用于存储所有表的相关数据信息
                    table_info = {'row_datas': []}  # 用于存储存在关键字的行数据
                    for sheet_name, sheet_data in xls_data.items():
                        sheet_exist = False  # 某一个sheet中是否匹配了关键字
                        rows = sheet_data['rows']  # sheet对应的行
                        cols = sheet_data['cols']  # sheet对应的列
                        row_num = -1

                        for row in sheet_data['content']:
                            row_num += 1
                            keyword_position = {}  # 关键字位置，与对应的值
                            row_exist = False  # 某一行是否匹配了关键字
                            if keyword in row:
                                keyword_position = [i for i, v in enumerate(row) if v == keyword]
                                sheet_exist = True  # 该sheet中是否匹配了关键字
                                row_exist = True  # 该行存在关键字的匹配
                                # 对存在匹配行的一行数据进行存储
                                row_data = [row_num + 1] + row
                                deal_str = u'<span style="color: red">' + keyword + u'</span>'  # 将匹配的关键字添加相应的html标签,以显示红色
                                for i in keyword_position:
                                    row_data[i+1] = deal_str
                                table_info['row_datas'].append(row_data)  # 将本行数据添加至存在关键字行列表中
                        if sheet_exist:
                            table_info['head'] = ['行号'] + sheet_data['header']  # 存储表头信息
                            table_info['colarray'] = [''] + num_converted_into_letters(cols) # 列标签'',  '', '', 'A', 'B', 'C'...
                            table_info['table_name'] = xls['tname']  # 关键字存在的表名
                            table_info['sheet_name'] = sheet_name  # 关键字存在的sheet名
                            context['datas'].append(table_info)  # 将存在关键字的表的相关信息存储
                    if context['datas']:
                        not_found = False
                        json_str = json.dumps(context)
                        send_msg(connection, json_str)
                        res['datas'] += context['datas']
        if not_found:
            context['type'] = 'not_found'
            json_str = json.dumps(context)
            send_msg(connection, json_str)
        return res
    else:
        pass


def send_msg1(conn, msg_bytes):
    """
    WebSocket服务端向客户端发送消息
    :param conn: 客户端连接到服务器端的socket对象,即： conn,address = socket.accept()
    :param msg_bytes: 向客户端发送的字节
    :return:
    """
    import struct

    if isinstance(msg_bytes, dict):
        msg_bytes = json.dumps(msg_bytes)

    token = b"\x81"
    length = len(msg_bytes)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)

    msg = token + msg_bytes
    conn.send(msg)
    return True

def send_msg(conn, msg_bytes):
    """
    WebSocket服务端向客户端发送消息
    :param conn: 客户端连接到服务器端的socket对象,即： conn,address = socket.accept()
    :param msg_bytes: 向客户端发送的字节
    :return:
    """
    import struct

    token = b"\x81"
    length = len(msg_bytes)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)

    msg = token + msg_bytes
    conn.send(msg)
    return True

def deal_tuple(keyword_tuple, query_mode):
    result = u''
    keyword_prefix = u'<span style="color: red">'
    keyword_suffix = u'</span>'
    # 1: 模糊查询; 2: 精确查询; 其余保留
    if query_mode == '1':
        for i in range(len(keyword_tuple)):
            if i % 2 == 1:
                result += (keyword_prefix + keyword_tuple[i] + keyword_suffix)
            else:
                if keyword_tuple[i] == u'':
                    continue
                else:
                    result += keyword_tuple[i]
        return result
    elif query_mode == '2':
        return keyword_prefix + keyword_tuple[0] + keyword_suffix
    else:
        pass


def advanced_search(keyword1, keyword2):
    # 高级检索
    # 表中一行数据包含多个关键字
    # 表中一行数据包含多个关键字中的至少一个

    context = {}
    context['datas'] = []
    exist = False
    exist_row = False

    keyword1_re = building_regular_expressions(keyword1)
    keyword2_re = building_regular_expressions(keyword2)

    keywords_re = [keyword1_re, keyword2_re]

    start = time.clock()
    filepath = r'F:\Project\G48\导表3'  # 自动转化成utf-8的字节字符串
    filepath = filepath.decode('utf-8')  # 形成无编码的unicode字符集
    pathDir = os.listdir(filepath)  # 目录下的所有文件

    for allDir in pathDir:
        child = os.path.join(filepath, allDir)  # 文件的完整路径
        if os.path.isfile(child):  # 判断路径是不是文件
            exist = False
            table_info = {}
            table_info['row_datas'] = []
            table_info['col'] = []
            workbook = xlrd.open_workbook(child)  # excel表
            sheets = workbook.sheets()  # 表中所有sheet
            for sheet in sheets:
                rows = sheet.nrows  # sheet对应的行
                cols = sheet.ncols  # sheet对应的列
                for row in range(rows):
                    exist_row = True               # exist表示一行元素包含所有的关键字
                    col_list = []
                    for keyword in keywords_re:
                        is_contain, col = contain(keyword, sheet.row_values(row))
                        if not is_contain:  # 一行元素不包含关键字keyword的模糊查询
                            exist_row = False
                            break
                        else:
                            if col >= 0:
                                col_list.append(col+3)
                    if exist_row:
                        # print sheet.row_values(row)
                        print col_list
                        exist = True
                        row_data = [allDir, sheet.name, row + 1] + sheet.row_values(row)
                        table_info['row_datas'].append(row_data)
                        table_head = ['表名', 'Sheet名', '行号']
                        table_info['head'] = table_head + sheet.row_values(0)
                        # table_info['col'] = col_list
                        table_info['col'].append(col_list)                   # 显示红色的位置
                        table_info['colarray'] = ['', '', '']
                        table_info['colarray'] += num_converted_into_letters(len(sheet.row_values(row)))
                        table_info['table_name'] = allDir
                        table_info['sheet_name'] = sheet.name
            if exist:
                context['datas'].append(table_info)
                print context['datas']
    end = time.clock()
    print "查询所花费的时间：%f" % (end - start)
    return context


def contain(pattern, row_elements):
    # 表格中的一行元素是否包含某个关键字
    # pattern: 匹配模式
    # row_elements: 待匹配的字符串元素列表
    col = -1
    for element in row_elements:
        if isinstance(element, float):
            element = str(element)
        elif isinstance(element, int):
            element = str(element)
        else:
            pass
        if pattern.match(element):
            col = row_elements.index(element)
            return True, col
    return False, col


def num_converted_into_letters(num):
    # 如将数字1，2，3...转化成A，B，C... 27转化成AA....
    # 最大列为26*26
    result = []
    for i in range(num):
        result.append(get_column_letter(i+1))
    return result


# def get_login(realm, username, may_save):
#     # retcode = True    #True，如果需要验证；否则用False
#     # username = '1357211280@qq.com'    #用户名
#     # password = 'p1357211280x'    #密码
#     # save = False    #True，如果想之后都不用验证；否则用False
#     # return retcode, username, password, save
#     return realm, username, password, may_save

def get_login(realm, username, may_save):
    return True, '1357211280@qq.com', 'p1357211280x', False


def ssl_server_trust_prompt( trust_dict ):
    return (True, trust_dict["failures"], True)


def update_svn(update_info):
    # svnurl = 'https://github.com/CMDXiong/excel.git'  # 远程仓库
    # outpath = 'F:\Project\pan_test_7'  # 下拉存储到本地的位置
    name = update_info['name']
    svnurl = update_info['host']
    outpath = update_info['localRoad']
    username = update_info['username']
    password = update_info['password']

    client = pysvn.Client()
    client.callback_get_login = get_login
    # client.callback_get_login = get_login(username=username, save=False, retcode=True, password=password)
    client.callback_ssl_server_trust_prompt = ssl_server_trust_prompt

    # 如果没有配置文件，提示建立配置文件
    # 否则，读取配置文件的相关信息
    # 判断相关地方的状态是否有改变，如果有，点击更新才有更新，否则直接退出，并且报告，已经是最新
    # changes = client.status('./examples/pysvn')

    client.checkout(svnurl, outpath)                  # 检出最新版本
    #client.checkout(svnurl, outpath, revision=rv)    # 检出指定版本

    # changes = client.status('./test') # 检测状态，获取各种新增、删除、修改、冲突、未版本化的状态
    # for f in changes:
    #     if f.text_status == pysvn.wc_status_kind.added:
    #         print f.path, 'A'
    #     elif f.text_status == pysvn.wc_status_kind.deleted:
    #         print f.path, 'D'
    #     elif f.text_status == pysvn.wc_status_kind.modified:
    #         print f.path, 'M'
    #     elif f.text_status == pysvn.wc_status_kind.conflicted:
    #         print f.path, 'C'
    #     elif f.text_status == pysvn.wc_status_kind.unversioned:
    #         print f.path, 'U'


def config(request):
    # 配置函数
    print '这是itoldskjaf一个测试'
    write_config_file()
    update_svn()
    return HttpResponse("更新完成")


def write_config_file():
    config1 = ConfigParser.RawConfigParser()
    print config1
    print type(config1)

    # 两个部分sections  每个section下都会有options 和对应的values
    list1 = [1,3,4]
    try:
        config1.add_section('remote')
        config1.set('remote', 'list', list1)
        config1.set('remote', 'url', 'https://github.com/CMDXiong/excel.git')
        config1.set('remote', 'outpath', 'C:\Users\panxiong\Desktop\pan_test_4')
        config1.set('remote', 'username', '1357211280@qq.com')
        config1.set('remote', 'password', '*****')

        config1.add_section('Section2')
        config1.set('Section2', 'ASC', '101')
        config1.set('Section2', 'AGD', '102')
        config1.set('Section2', 'AJX', '103')
        config1.set('Section2', 'AGX', '104')

        '''
        sections options   has_section  has_option
        '''
        sections = config1.sections()  # 返回section列表
        print sections
        for i in range(len(sections)):
            temp = sections[i]
            print temp
            options = config1.options(temp)
            for j in range(len(options)):
                key_value = '%s = %s' % (options[j], config1.get(temp, options[j]))  # 取值，取option
                print key_value

        flag = config1.has_section('remote')
        print flag
        flag1 = config1.has_option('Section2', 'ASC')  # 判断是否存在
        print flag1

        item = config1.items('remote')  # 返回键值列表

        config1.set('Section2', 'ASC', '4242')  # 修改
    except Exception, e:
        print str(e)

    # Writing our configuration file to 'example.cfg'
    with open(r'F:\ProjectTest\example1.cfg', 'wb') as configfile:
        config1.write(configfile)

