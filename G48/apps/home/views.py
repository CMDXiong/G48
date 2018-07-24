# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse

import xlrd
import time
import os
import string
import re

import pysvn
import ConfigParser
import exceptions
from zipfile import BadZipfile

import openpyxl
# from openpyxl.reader.excel import load_workbook
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, column_index_from_string


def test(request):
    context = {'test': "panxiong"}
    return render(request, 'home/index.html', context=context)


def search_result(request):
    # 搜索结果函数
    keyword = request.POST['content']                   # 获取关键字
    keyword = keyword.replace(' ', '')                  # 去掉关键字中的所有空格
    inquiry_mode = request.POST['inquiry_mode']         # 获取查询方式
    print request.POST['tableType']
    context = {}                                        # 传入到html模板中的数据
    print keyword
    print inquiry_mode

    if cmp(inquiry_mode, '1') == 0:                      # 模糊查询
        print '1'
        context = fuzzy_query_1(keyword)
    elif cmp(inquiry_mode, '2') == 0:                    # 精确查询
        print '2'
        context = perfect_match(keyword)
    elif cmp(inquiry_mode, '3') == 0:                    # 高级查询
        print '3'
        keyword1 = u'商会'.replace(' ', '')
        keyword2 = u'队伍'.replace(' ', '')
        context = advanced_search(keyword1, keyword2)  # 高级查询，可以同时查询多个关键字
    else:
        print "4"
    return render(request, 'home/index.html', context=context)


def index(request):
    # complete_file_name = ur'F:\Project\H37\H37_xls_search\04GamePlay\02狩猎活动\01异常行为研究\02_c巨兽挑战玩法参数表.xlsx'
    # file_name = u'02_c巨兽挑战玩法参数表.xlsx'
    # pattern = building_regular_expressions(u'奖励周期限制类型')
    # wb = load_workbook(complete_file_name)
    # table_info = {'row_datas': []}
    # sheets = wb.worksheets  # 所有的sheet表
    # for sheet in sheets:
    #     # 获取行列数
    #     row1 = sheet.max_row
    #     column2 = sheet.max_column
    #     print row1, column2, sheet.min_row, sheet.min_column
    #     for row in sheet.rows:
    #         for cell in row:
    #             row_num = cell.row  # 行号
    #             col_num = column_index_from_string(cell.column)  # 列号
    #             # print complete_file_name
    #             print row_num, col_num, cell.value, type(cell.value)
    #             resultstr = u''
    #
    #             if cell.value is None:
    #                 continue
    #             elif isinstance(cell.value, (float, int, long)):
    #                 resultstr = str(cell.value)
    #             else:
    #                 resultstr = cell.value
    #
    #             # print row_num, col_num, cell.value, type(cell.value)
    #             if pattern.match(resultstr):
    #                 m = pattern.match(resultstr)
    #                 deal_str = deal_tuple(m.groups())  # 将关键字添加相应的html标签
    #                 exist = True
    #                 row_data = [file_name, sheet.title, row_num]
    #                 temp_data = [i.value for i in row]
    #                 row_data += temp_data
    #                 row_data[col_num + 2] = deal_str              # openpyxl中的行，列都是从1开始
    #                 table_info['row_datas'].append(row_data)
    #                 table_head = ['表名', 'Sheet名', '行号']
    #                 temp_head = [i.value for i in list(sheet.rows)[0]]
    #                 print 'temp_head', temp_head
    #                 table_info['head'] = table_head + temp_head
    #                 table_info['colarray'] = ['', '', '']
    #                 table_info['colarray'] += num_converted_into_letters(len(list(row)))
    #                 table_info['table_name'] = file_name
    #                 table_info['sheet_name'] = sheet.title                        # sheet.title 可以获取sheet名
    # except (BadZipfile, TypeError, IOError):
    #     print "出错的文件："

    keyword = u'玩家每天最多完成'
    context = read_xlsx_file(filepath, keyword)
    # context = {'datas': [table_info]}
    return render(request, 'home/index.html', context=context)


def perfect_match(keyword):
    # 完全匹配
    context = {}
    context['datas'] = []
    # table_head = []
    start = time.clock()
    filepath = r'F:\Project\G48\导表3'   # 自动转化成utf-8的字节字符串
    filepath = filepath.decode('utf-8')  # 形成无编码的unicode字符集
    pathDir = os.listdir(filepath)       # 目录下的所有文件
    exist = False                        # 某一行中存在关键字

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
                    col_list = []          # 一行中存在关键字的col集合
                    for col in range(cols):
                        if cmp(sheet.cell_value(row, col), keyword) == 0:  # 查询row行，col列的值是否与关键字匹配
                            exist = True
                            row_data = [allDir, sheet.name, row + 1] + sheet.row_values(row)
                            keyword_prefix = u'<span style="color: red">'
                            keyword_suffix = u'</span>'
                            row_data[col+3] = keyword_prefix + row_data[col+3] + keyword_suffix
                            print row_data
                            table_info['row_datas'].append(row_data)
                            table_head = ['表名', 'Sheet名', '行号']
                            table_info['head'] = table_head + sheet.row_values(0)
                            # table_info['col'] += [col + 3, ]
                            col_list.append(col+3)
                            table_info['colarray'] = ['', '', '']
                            table_info['colarray'] += num_converted_into_letters(len(sheet.row_values(row)))
                            table_info['table_name'] = allDir
                            table_info['sheet_name'] = sheet.name
                    if exist:
                        table_info['col'].append(col_list)  # 显示红色的位置
            if exist:
                context['datas'].append(table_info)
    return context


# 为keyword关键字的模糊查询建立查询模式。
# 例如"潘雄"，最后建立的模式为：
# ur'[\s\w|\u4e00-\u9fa5|，。；？！]*?潘[\s\w|\u4e00-\u9fa5|，。；？！]*?雄[\s\w|\u4e00-\u9fa5|，。；？！]*?'
def building_regular_expressions(keyword):
    # 在这里应该首先检查keyword是否是字符串，这点可以留做以后补充
    if not isinstance(keyword, (str, unicode, int, float)):
        raise TypeError('bad operand type')
    # text = u'我是潘sdf是雄'
    # str1 = u"潘雄"
    insert_pattern = u'([\s\w|\u4e00-\u9fa5|，。；？！]*?)'     # 非贪婪匹配 基本汉字的unicode编码是4E00-9FA5
    pattern = insert_pattern
    for i in range(len(keyword)):
        pattern += (u'(' + keyword[i] + u')' + insert_pattern)
    # if re.match(pattern, u'我是潘d是s，雄'):  # 这个用例用作测试，暂时不要删除
    #     print '测试成功'
    # else:
    #     print '测试失败'
    re_pattern = re.compile(pattern)
    # if re_pattern.match(text):
    #     print 'ok'
    return re_pattern


filepath = ur'F:\Project\H37\H37_xls_search\04GamePlay\02狩猎活动\01异常行为研究'   # unicode编码


def read_xlsx_file(file_path, keyword):
    pattern = pattern = building_regular_expressions(keyword)
    exist = False                                                        # 关键字是否存在某一行
    context = {'datas': []}

    if os.path.isfile(file_path):                                        # 如果是文件
        if '\\' in file_path:
            file_name = file_path.split('\\')[-1]
        else:
            file_name = file_path
        print 'file_name', file_name
        wb = load_workbook(file_path)
        table_info = {'row_datas': []}
        try:
            sheets = wb.worksheets  # 所有的sheet表
        except (BadZipfile, TypeError, IOError):
            print "出错的文件："
            print file_path
        for sheet in sheets:
            # 获取行列数
            row1 = sheet.max_row
            column2 = sheet.max_column
            print row1, column2, sheet.min_row, sheet.min_column
            for row in sheet.rows:
                for cell in row:
                    row_num = cell.row  # 行号
                    col_num = column_index_from_string(cell.column)  # 列号
                    # print complete_file_name
                    print row_num, col_num, cell.value, type(cell.value)
                    resultstr = u''

                    if cell.value is None:
                        continue
                    elif isinstance(cell.value, (float, int, long)):
                        resultstr = str(cell.value)
                    else:
                        resultstr = cell.value

                    # print row_num, col_num, cell.value, type(cell.value)
                    if pattern.match(resultstr):
                        m = pattern.match(resultstr)
                        deal_str = deal_tuple(m.groups())  # 将关键字添加相应的html标签
                        exist = True
                        row_data = [file_name, sheet.title, row_num]
                        temp_data = [i.value for i in row]
                        row_data += temp_data
                        row_data[col_num + 2] = deal_str              # openpyxl中的行，列都是从1开始
                        table_info['row_datas'].append(row_data)
                        table_head = ['表名', 'Sheet名', '行号']
                        temp_head = [i.value for i in list(sheet.rows)[0]]
                        table_info['head'] = table_head + temp_head
                        table_info['colarray'] = ['', '', '']
                        table_info['colarray'] += num_converted_into_letters(len(list(row)))
                        table_info['table_name'] = file_name
                        table_info['sheet_name'] = sheet.title                        # sheet.title 可以获取sheet名
        context['datas'].append(table_info)
    elif os.path.isdir(file_path):  # 如果是路径
        g = os.walk(file_path)
        # path 一个目录
        # d:代表path目录所有的目录(只包含名字，不包含前面的路径)
        # filelist: 代表path目录所有的文件(也只包含名字)
        for path, dir_list, file_name_list in g:
            for file_name in file_name_list:
                if os.path.splitext(file_name)[1] == '.xlsx':  # 是.xlsx文件
                    complete_file_name = os.path.join(path, file_name)  # 文件的完整路径名
                    try:
                        wb = load_workbook(complete_file_name)
                    except (BadZipfile, TypeError, IOError):
                        print "出错的文件："
                        print complete_file_name
                    table_info = {'row_datas': []}
                    sheets = wb.worksheets  # 所有的sheet表
                    for sheet in sheets:
                        for row in sheet.rows:
                            for cell in row:
                                row_num = cell.row                           # 行号
                                col_num = column_index_from_string(cell.column)    # 列号
                                resultstr = u''
                                if cell.value is None:
                                    continue
                                elif isinstance(cell.value, (float, int, long)):
                                    resultstr = str(cell.value)
                                else:
                                    resultstr = cell.value
                                if pattern.match(resultstr):
                                    print 'success'
                                    m = pattern.match(resultstr)
                                    deal_str = deal_tuple(m.groups())  # 将关键字添加相应的html标签
                                    exist = True
                                    row_data = [file_name, sheet.title, row_num]
                                    temp_data = [i.value for i in row]
                                    row_data += temp_data
                                    row_data[col_num + 2] = deal_str  # openpyxl中的行，列都是从1开始
                                    table_info['row_datas'].append(row_data)
                                    table_head = ['表名', 'Sheet名', '行号']
                                    temp_head = [i.value for i in list(sheet.rows)[0]]
                                    table_info['head'] = table_head + temp_head
                                    table_info['colarray'] = ['', '', '']
                                    table_info['colarray'] += num_converted_into_letters(len(list(row)))
                                    table_info['table_name'] = file_name
                                    table_info['sheet_name'] = sheet.title  # sheet.title 可以获取sheet名
                    if exist:
                        context['datas'].append(table_info)
                elif os.path.splitext(file_name)[1] == '.xls':  # 是.xls文件
                    pass
                elif os.path.splitext(file_name)[1] == '.cvs':  # 是.xls文件
                    pass
                else:
                    print "文件格式不在.xlsx .xls, .cvs之中"
                    pass
    else:
        print "找不到文件或路径"
    return context


# 模糊匹配
def fuzzy_query_1(keyword):
    if not isinstance(keyword, (str, unicode, int, float)):
        raise TypeError('bad operand type')

    context = {}
    context['datas'] = []
    pattern = building_regular_expressions(keyword)
    filepath = r'F:\Project\G48\导表3'   # 自动转化成utf-8的字节字符串
    filepath = filepath.decode('utf-8')  # 形成无编码的unicode字符集
    pathDir = os.listdir(filepath)       # 目录下的所有文件

    exist = False                        # 关键字是否存在某一行
    for allDir in pathDir:
        child = os.path.join(filepath, allDir)  # 文件的完整路径
        if os.path.isfile(child):               # 判断路径是不是文件
            exist = False
            table_info = {}
            table_info['row_datas'] = []
            table_info['col'] = []
            workbook = xlrd.open_workbook(child)  # excel表
            sheets = workbook.sheets()            # 表中所有sheet
            for sheet in sheets:
                rows = sheet.nrows  # sheet对应的行
                cols = sheet.ncols  # sheet对应的列
                for row in range(rows):
                    col_list = []
                    for col in range(cols):
                        result = sheet.cell_value(row, col)
                        resultstr = u''
                        if isinstance(result, float):
                            resultstr = str(result)
                        elif isinstance(result, int):
                            resultstr = str(result)
                        else:
                            resultstr = result
                        if pattern.match(resultstr):
                            m = pattern.match(resultstr)
                            deal_str = deal_tuple(m.groups())     # 将关键字添加相应的html标签
                            exist = True
                            row_data = [allDir, sheet.name, row+1] + sheet.row_values(row)
                            row_data[col+3] = deal_str
                            table_info['row_datas'].append(row_data)
                            table_head = ['表名', 'Sheet名', '行号']
                            table_info['head'] = table_head + sheet.row_values(0)
                            # table_info['col'] += [col + 3, ]
                            col_list.append(col + 3)
                            table_info['colarray'] = ['', '', '']
                            table_info['colarray'] += num_converted_into_letters(len(sheet.row_values(row)))
                            table_info['table_name'] = allDir
                            table_info['sheet_name'] = sheet.name
                    if exist:
                        table_info['col'].append(col_list)  # 显示红色的位置
            if exist:
                context['datas'].append(table_info)
    return context


def deal_tuple(keyword_tuple):
    result = u''
    keyword_prefix = u'<span style="color: red">'
    keyword_suffix = u'</span>'
    for i in range(len(keyword_tuple)):
        if i % 2 == 1:
            result += (keyword_prefix + keyword_tuple[i] + keyword_suffix)
        else:
            if keyword_tuple[i] == u'':
                continue
            else:
                result += keyword_tuple[i]
    return result


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
    if num > 26*26 or num <= 0:
        return None
    chart_list = list('abcdefghijklmnopqrstuvwxyz'.upper())
    if num <= 26:
        return list('abcdefghijklmnopqrstuvwxyz'.upper()[:num])
    else:
        result = chart_list
        for i in range(num-26):
            temp_str = chart_list[(i+27)/26 - 1] + chart_list[(i+27) % 26 - 1]
            result.append(temp_str)
        return result


def fuzzy_query():
    # 模糊匹配
    start = time.clock()
    filepath = r'F:\Project\G48\导表3'  # 自动转化成utf-8的字节字符串
    filepath = filepath.decode('utf-8')  # 形成无编码的unicode字符集
    pathDir = os.listdir(filepath)  # 目录下的所有文件

    searchStr = u"不在商会不能创建队伍"  # 查询的字符串（关键字）

    for allDir in pathDir:
        child = os.path.join(filepath, allDir)  # 文件的完整路径
        if os.path.isfile(child):  # 判断路径是不是文件
            workbook = xlrd.open_workbook(child)  # excel表
            sheets = workbook.sheets()  # 表中所有sheet
            for sheet in sheets:
                rows = sheet.nrows  # sheet对应的行
                cols = sheet.ncols  # sheet对应的列
                for row in range(rows):
                    for col in range(cols):
                        result = sheet.cell_value(row, col)
                        resultstr = u''
                        if isinstance(result, float):
                            resultstr = str(result)
                        elif isinstance(result, int):
                            resultstr = str(result)
                        else:
                            resultstr = result
                        # if resultstr.find(searchStr) != -1:
                        #     print '潘雄'
                        if string.find(resultstr, searchStr) != -1:
                            print "潘雄"
                            print sheet.row_values(row)  # 得到row行的所有数据
                            print "关键字：%s" % sheet.cell_value(row, col).encode('utf-8')
                            print
                            print "以下是查询结果："
                            print "表名: %s" % child.encode('utf-8')
                            print "sheet名：%s" % sheet.name.encode('utf-8')
                            print "位置：row = %d, col = %d" % (row + 1, col + 1)
    end = time.clock()
    print "查询所花费的时间：%f" % (end - start)


def get_login(realm, username, may_save):
    retcode = True    #True，如果需要验证；否则用False
    username = '1357211280@qq.com'    #用户名
    password = 'p1357211280x'    #密码
    save = False    #True，如果想之后都不用验证；否则用False
    return retcode, username, password, save


def ssl_server_trust_prompt( trust_dict ):
    return (True, trust_dict["failures"], True)


def update_svn():
    client = pysvn.Client()
    client.callback_get_login = get_login
    client.callback_ssl_server_trust_prompt = ssl_server_trust_prompt

    # 如果没有配置文件，提示建立配置文件
    # 否则，读取配置文件的相关信息
    # 判断相关地方的状态是否有改变，如果有，点击更新才有更新，否则直接退出，并且报告，已经是最新
    # changes = client.status('./examples/pysvn')

    svnurl = 'https://github.com/CMDXiong/excel.git'               # 远程仓库
    outpath = 'C:\Users\panxiong\Desktop\pan_test_4'               # 下拉存储到本地的位置

    changes = client.status('./examples/pysvn')
    client.checkout(svnurl, outpath)


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
