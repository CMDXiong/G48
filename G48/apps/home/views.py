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
from zipfile import BadZipfile

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, column_index_from_string
import unicodecsv as csv
# import csv
import chardet

import reader

global_data = {}


def test(request):
    context = {'test': "panxiong"}
    return render(request, 'home/index.html', context=context)


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
        # context = fuzzy_query_1(keyword)
        global global_data
        # print global_data
        start1 = time.clock()
        context = fuzzy_query(keyword, global_data)
        print context
        end1 = time.clock()
        print '查找的时间：', end1 - start1
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


keyword = u'匹配流言'
filepath = ur'F:\Project\H37\H37_xls_search\06需求文档\[H37]NPC需求--11月.xlsx'   # unicode编码
# filepath = ur'F:\Project\H37\H37_xls_search\05Data'   # unicode编码
def index(request):
    # xls = reader.read_file_xls(filepath)
    xls = reader.read_file_xlsx(filepath)
    # xls = reader.read_file_csv(filepath)
    start = time.clock()
    global global_data
    # global_data = datas_form_files(filepath)
    end = time.clock()
    print end - start
    context = {}
    # context = parse_file(filepath, keyword)
    return render(request, 'home/index.html', context=context)


def datas_form_files(file_path):
    files_counts = 0
    datas = []                                                           # 每一个元素都是一个表的字典
    if os.path.isfile(file_path):                                        # 如果是文件
        files_counts += 1
        file_name = os.path.basename(file_path)                          # 得到一个路径下的文件名
        name, ext = os.path.splitext(file_path)                          # ext为文件的扩展名
        if ext == '.xlsx':                                               # 是.xlsx文件
            xlsx_data = reader.read_file_xlsx(file_path)
            if xlsx_data:
                datas.append(xlsx_data)
        elif ext == '.xls':                                              # 是.xls文件
            xls_result = reader.read_file_xls(file_path)
            if xls_result:
                datas.append(xls_result)
        elif ext == '.csv':                                              # 是.xlsx文件
            csv_result = reader.read_file_csv(file_path)
            if csv_result:
                datas.append(csv_result)
        else:                                                # 不属于.xlsx，.xls，.csv文件格式
            print "文件格式不在.xlsx，.xls, .csv之中"
    elif os.path.isdir(file_path):  # 如果是路径
        g = os.walk(file_path)
        # path 一个目录
        # d:代表path目录所有的目录(只包含名字，不包含前面的路径)
        # filelist: 代表path目录所有的文件(也只包含名字)
        for path, dir_list, file_name_list in g:
            for file_name in file_name_list:
                complete_file_name = os.path.join(path, file_name)  # 文件的完整路径名
                # table_info = {'row_datas': []}
                # exist = False
                files_counts += 1
                if os.path.splitext(file_name)[1] == '.xlsx':  # 是.xlsx文件
                    xlsx_data = reader.read_file_xlsx(complete_file_name)
                    if xlsx_data:
                        datas.append(xlsx_data)
                elif os.path.splitext(file_name)[1] == '.xls':  # 是.xls文件
                    xls_result = reader.read_file_xls(complete_file_name)
                    if xls_result:
                        datas.append(xls_result)
                elif os.path.splitext(file_name)[1] == '.csv':  # 是.csv文件
                    csv_result = reader.read_file_csv(complete_file_name)
                    if csv_result:
                        datas.append(csv_result)
                else:
                    print "文件格式不在.xlsx .xls, .cvs之中"
    else:
        print "找不到文件或路径"
    print files_counts
    return datas

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
    if not isinstance(keyword, (str, unicode, int, float, long)):
        raise TypeError('bad operand type')
    insert_pattern = u'([\s\w|\u4e00-\u9fa5|，。；;,.:？！]*?)'     # 非贪婪匹配 基本汉字的unicode编码是4E00-9FA5
    pattern = insert_pattern
    for i in range(len(keyword)):
        pattern += (u'(' + keyword[i] + u')' + insert_pattern)
    re_pattern = re.compile(pattern)
    return re_pattern


def parse_file(file_path, keyword):
    context = {'datas': []}
    if os.path.isfile(file_path):                                        # 如果是文件
        file_name = os.path.basename(file_path)                          # 得到一个路径下的文件名
        name, ext = os.path.splitext(file_path)                          # ext为文件的扩展名

        if ext == '.xlsx':                                               # 是.xlsx文件
            xlsx_result = parse_file_xlsx(file_path, keyword)
            if xlsx_result:
                context['datas'] += xlsx_result['datas']
        elif ext == '.xls':                                              # 是.xls文件
            xls_result = parse_file_xls(file_path, keyword)
            if xls_result:
                context['datas'] += xls_result['datas']
        elif ext == '.csv':                                              # 是.xlsx文件
            csv_result = parse_file_cvs(file_path, keyword)
            if csv_result:
                context['datas'] += csv_result['datas']
        else:                                                # 不属于.xlsx，.xls，.csv文件格式
            print "文件格式不在.xlsx，.xls, .csv之中"
    elif os.path.isdir(file_path):  # 如果是路径
        g = os.walk(file_path)
        # path 一个目录
        # d:代表path目录所有的目录(只包含名字，不包含前面的路径)
        # filelist: 代表path目录所有的文件(也只包含名字)
        for path, dir_list, file_name_list in g:
            for file_name in file_name_list:
                complete_file_name = os.path.join(path, file_name)  # 文件的完整路径名
                # table_info = {'row_datas': []}
                # exist = False
                if os.path.splitext(file_name)[1] == '.xlsx':  # 是.xlsx文件
                    xlsx_result = parse_file_xlsx(complete_file_name, keyword)
                    if xlsx_result:
                        context['datas'] += xlsx_result['datas']
                elif os.path.splitext(file_name)[1] == '.xls':  # 是.xls文件
                    print '这是.xls'
                    xls_result = parse_file_xls(complete_file_name, keyword)
                    if xls_result:
                        context['datas'] += xls_result['datas']
                elif os.path.splitext(file_name)[1] == '.csv':  # 是.csv文件
                    csv_result = parse_file_cvs(complete_file_name, keyword)
                    if csv_result:
                        context['datas'] += csv_result['datas']
                else:
                    print "文件格式不在.xlsx .xls, .cvs之中"
    else:
        print "找不到文件或路径"
    return context


def parse_file_cvs(file_name, keyword):
    real_file_name = os.path.basename(file_name)          # 得到一个路径下的文件名
    pattern = building_regular_expressions(keyword)       # 生成关键字查询模式
    table_info = {'row_datas': []}                        # 用于存储存在关键字的行数据
    context = {'datas': []}
    sheet_exist = False                                         # 某一个sheet中是否匹配了关键字
    # 获取文件的编码方式
    csvfile_test_code = open(file_name, 'r')
    file_encoding = chardet.detect(csvfile_test_code.read())  # 获取文件的编码方式
    csvfile_test_code.close()

    # 以相对应的编码方式解析.csv文件
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile, encoding=file_encoding['encoding'])
        cur_line_num = 1                                      # 当前行号
        sheet_exist = False                                         # 某一个sheet中是否匹配了关键字
        max_col_num = 0                                       # 所有存在关键字行中的最大列数
        try:
            head_row = next(reader)                           # 表头数据
            for row in reader:                                # 从第一行开始遍历
                cur_line_num += 1                             # 当前行号
                cur_col_num = -1                            # 当前列号
                row_exist = False                             # 某一行是否匹配了关键字
                keyword_position = {}
                row_data = []
                for cell in row:
                    cur_col_num += 1
                    is_match = pattern.match(cell)            # 匹配结果
                    if is_match:                              # 如果存在匹配， 则记录该行的所有数据和相关信息
                        sheet_exist = True                          # 某一个sheet中是否匹配了关键字
                        row_exist = True                      # 某一行是否匹配了关键字
                        max_col_num = max_col_num if max_col_num > len(row) else len(row)  # 取得较大的列值
                        # 对存在匹配行的一行数据进行存储
                        keyword_red = deal_tuple(is_match.groups())                      # 将匹配的关键字添加相应的html标签,以显示红色
                        row_data = [real_file_name, real_file_name, cur_line_num] + row  # 前三个对应于表名，sheet名，行号
                        keyword_position[cur_col_num + 3] = keyword_red                  # 将关键字标红的数据替换原来的数据
                if row_exist:
                    for key, value in keyword_position.items():                          # 对所有关键字进行相应的替换
                        row_data[key] = value
                    table_info['row_datas'].append(row_data)  # 将本行数据添加至存在关键字行列表中
        except UnicodeDecodeError:
            print '编码出错的文件：'
            print file_name
        if sheet_exist:
            table_info['head'] = ['表名', 'Sheet名', '行号'] + head_row  # 存储表头信息
            table_info['colarray'] = ['', '', ''] + num_converted_into_letters(max_col_num)  # 列标签'',  '', '', 'A', 'B', 'C'...
            table_info['table_name'] = real_file_name  # 关键字存在的表名
            table_info['sheet_name'] = real_file_name  # 关键字存在的sheet名
            context['datas'].append(table_info)
    if context['datas']:
        return context
    else:
        return None


def parse_file_xlsx(file_name, keyword):
    real_file_name = os.path.basename(file_name)          # 得到一个路径下的文件名
    pattern = building_regular_expressions(keyword)       # 生成关键字查询模式
    table_info = {'row_datas': []}                        # 用于存储存在关键字的行数据
    context = {'datas': []}                               # 用于存储所有表的相关数据信息
    sheet_exist = False                                   # 某一个sheet中是否存在关键字
    wb = load_workbook(file_name)                         # 得到一个excel表的对象
    try:
        sheets = wb.worksheets                            # 所有的sheet表
    except (BadZipfile, TypeError, IOError):
        print "出错的文件："
        print file_name
    for sheet in sheets:
        sheet_exist = False                                            # 某一个sheet中是否存在关键字
        max_col_num = 0                                          # 所有存在关键字行中的最大列数
        for row in sheet.rows:
            row_exist = False                                    # 某一行是否匹配了关键字
            keyword_position = {}
            row_data = []
            for cell in row:
                row_num = cell.row                               # 行号
                col_num = column_index_from_string(cell.column)  # 列号
                if cell.value is None:
                    continue
                elif isinstance(cell.value, (float, int, long)):
                    resultstr = str(cell.value)
                else:
                    resultstr = cell.value

                is_match = pattern.match(resultstr)              # 匹配结果
                if is_match:                                     # 如果存在匹配， 则记录该行的所有数据和相关信息
                    sheet_exist = True                                 # 此sheet中匹配了关键字
                    row_exist = True                             # 此行是匹配了关键字
                    max_col_num = max_col_num if max_col_num > len(list(row)) else len(list(row))  # 取得较大的列值
                    # 对存在匹配行的一行数据进行存储
                    row_data = [real_file_name, sheet.title, row_num] + [i.value for i in row]  # 前三个对应于表名，sheet名，行号
                    deal_str = deal_tuple(is_match.groups())     # 将匹配的关键字添加相应的html标签,以显示红色
                    # row_data[col_num + 2] = deal_str           # 将关键字标红的数据替换原来的数据,openpyxl中的行，列都是从1开始,所以加的是2不是3
                    keyword_position[col_num + 2] = deal_str     # 将关键字标红的数据替换原来的数据，加的是3不是2，注意与openpyxl的区别
            if row_exist:
                for key, value in keyword_position.items():      # 对所有关键字进行相应的替换
                    row_data[key] = value
                table_info['row_datas'].append(row_data)         # 将本行数据添加至存在关键字行列表中
        # 存储每一个table中sheet的信息
        if sheet_exist:
            table_info['head'] = ['表名', 'Sheet名', '行号'] + [i.value for i in list(sheet.rows)[0]]  # 存储表头信息
            table_info['colarray'] = ['', '', ''] + num_converted_into_letters(max_col_num)            # 列标签'',  '', '', 'A', 'B', 'C'...
            table_info['table_name'] = real_file_name                                                  # 关键字存在的表名
            table_info['sheet_name'] = sheet.title                                                     # 关键字存在的sheet名
            context['datas'].append(table_info)
    if context['datas']:
        return context
    else:
        return None


def fuzzy_query(keyword, datas):
    res = {'datas': []}
    pattern = building_regular_expressions(keyword)  # 生成关键字查询模式
    for xls in datas:
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
                for item in row:
                    resultstr = u''
                    if item is None:
                        continue
                    if isinstance(item, float):
                        resultstr = str(item)
                    elif isinstance(item, (int, long)):
                        resultstr = str(item)
                    else:
                        resultstr = item

                    is_match = pattern.match(resultstr)  # 匹配结果
                    if is_match:  # 如果存在匹配， 则记录该行的所有数据和相关信息
                        sheet_exist = True  # 该sheet中是否匹配了关键字
                        row_exist = True  # 该行存在关键字的匹配
                        # 对存在匹配行的一行数据进行存储
                        row_data = [xls['tname'], sheet_name, row_num + 1] + sheet_data['content'][row_num]
                        deal_str = deal_tuple(is_match.groups())  # 将匹配的关键字添加相应的html标签,以显示红色
                        print deal_str
                        col = row.index(item)
                        keyword_position[col + 3] = deal_str  # 将关键字标红的数据替换原来的数据，加的是3不是2，注意与openpyxl的区别
                if row_exist:
                    for key, value in keyword_position.items():  # 对所有关键字进行相应的替换
                        row_data[key] = value
                    table_info['row_datas'].append(row_data)  # 将本行数据添加至存在关键字行列表中

            # for row in range(rows):
            #     keyword_position = {}  # 关键字位置，与对应的值
            #     row_exist = False  # 某一行是否匹配了关键字
            #     for col in range(cols):
            #         result = sheet_data['content'][row][col]
            #         print type(result)
            #         resultstr = u''
            #         if result is None:
            #             continue
            #         if isinstance(result, float):
            #             resultstr = str(result)
            #         elif isinstance(result, (int, long)):
            #             resultstr = str(result)
            #         else:
            #             resultstr = result
            #         print 'resultstr', type(resultstr)
            #
            #         is_match = pattern.match(resultstr)  # 匹配结果
            #         if is_match:  # 如果存在匹配， 则记录该行的所有数据和相关信息
            #             sheet_exist = True  # 该sheet中是否匹配了关键字
            #             row_exist = True  # 该行存在关键字的匹配
            #             # 对存在匹配行的一行数据进行存储
            #             row_data = [xls['tname'], sheet_name, row + 1] + sheet_data['content'][row]
            #             deal_str = deal_tuple(is_match.groups())  # 将匹配的关键字添加相应的html标签,以显示红色
            #             keyword_position[col + 3] = deal_str      # 将关键字标红的数据替换原来的数据，加的是3不是2，注意与openpyxl的区别
            #     if row_exist:
            #         for key, value in keyword_position.items():  # 对所有关键字进行相应的替换
            #             row_data[key] = value
            #         table_info['row_datas'].append(row_data)     # 将本行数据添加至存在关键字行列表中
            if sheet_exist:
                table_info['head'] = ['表名', 'Sheet名', '行号'] + sheet_data['header']  # 存储表头信息
                table_info['colarray'] = ['', '', ''] + num_converted_into_letters(
                    cols)  # 列标签'',  '', '', 'A', 'B', 'C'...
                table_info['table_name'] = xls['tname']  # 关键字存在的表名
                table_info['sheet_name'] = sheet_name  # 关键字存在的sheet名
                context['datas'].append(table_info)  # 将存在关键字的表的相关信息存储
        if context['datas']:
            res['datas'] += context['datas']
    return res


def parse_file_xls(file_name, keyword):
    real_file_name = os.path.basename(file_name)       # 得到一个路径下的文件名
    pattern = building_regular_expressions(keyword)    # 生成关键字查询模式
    table_info = {'row_datas': []}                     # 用于存储存在关键字的行数据
    context = {'datas': []}                            # 用于存储所有表的相关数据信息
    sheet_exist = False                                # 某一个sheet中是否匹配了关键字

    workbook = xlrd.open_workbook(file_name)           # excel表对象
    sheets = workbook.sheets()                         # 表中所有sheet
    for sheet in sheets:
        sheet_exist = False                            # 某一个sheet中是否匹配了关键字
        max_col_num = 0                                # 所有存在关键字行中的最大列数
        rows = sheet.nrows  # sheet对应的行
        cols = sheet.ncols  # sheet对应的列
        for row in range(rows):
            keyword_position = {}        # 关键字位置，与对应的值
            row_exist = False            # 某一行是否匹配了关键字
            for col in range(cols):
                result = sheet.cell_value(row, col)
                resultstr = u''
                if isinstance(result, float):
                    resultstr = str(result)
                elif isinstance(result, int):
                    resultstr = str(result)
                else:
                    resultstr = result

                is_match = pattern.match(resultstr)               # 匹配结果
                if is_match:                                      # 如果存在匹配， 则记录该行的所有数据和相关信息
                    sheet_exist = True                                  # 该sheet中是否匹配了关键字
                    row_exist = True                              # 该行存在关键字的匹配
                    max_col_num = max_col_num if max_col_num > len(sheet.row_values(row)) else len(sheet.row_values(row))  # 取得较大的列值
                    # 对存在匹配行的一行数据进行存储
                    row_data = [real_file_name, sheet.name, row + 1] + sheet.row_values(row)
                    deal_str = deal_tuple(is_match.groups())      # 将匹配的关键字添加相应的html标签,以显示红色
                    keyword_position[col + 3] = deal_str          # 将关键字标红的数据替换原来的数据，加的是3不是2，注意与openpyxl的区别
            if row_exist:
                for key, value in keyword_position.items():  # 对所有关键字进行相应的替换
                    row_data[key] = value
                table_info['row_datas'].append(row_data)          # 将本行数据添加至存在关键字行列表中
        if sheet_exist:
            table_info['head'] = ['表名', 'Sheet名', '行号'] + sheet.row_values(0)           # 存储表头信息
            table_info['colarray'] = ['', '', ''] + num_converted_into_letters(max_col_num)  # 列标签'',  '', '', 'A', 'B', 'C'...
            table_info['table_name'] = real_file_name                                        # 关键字存在的表名
            table_info['sheet_name'] = sheet.name                                            # 关键字存在的sheet名
            context['datas'].append(table_info)                                              # 将存在关键字的表的相关信息存储
    if context['datas']:
        return context
    else:
        return None


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


# def fuzzy_query():
#     # 模糊匹配
#     start = time.clock()
#     filepath = r'F:\Project\G48\导表3'  # 自动转化成utf-8的字节字符串
#     filepath = filepath.decode('utf-8')  # 形成无编码的unicode字符集
#     pathDir = os.listdir(filepath)  # 目录下的所有文件
#
#     searchStr = u"不在商会不能创建队伍"  # 查询的字符串（关键字）
#
#     for allDir in pathDir:
#         child = os.path.join(filepath, allDir)  # 文件的完整路径
#         if os.path.isfile(child):  # 判断路径是不是文件
#             workbook = xlrd.open_workbook(child)  # excel表
#             sheets = workbook.sheets()  # 表中所有sheet
#             for sheet in sheets:
#                 rows = sheet.nrows  # sheet对应的行
#                 cols = sheet.ncols  # sheet对应的列
#                 for row in range(rows):
#                     for col in range(cols):
#                         result = sheet.cell_value(row, col)
#                         resultstr = u''
#                         if isinstance(result, float):
#                             resultstr = str(result)
#                         elif isinstance(result, int):
#                             resultstr = str(result)
#                         else:
#                             resultstr = result
#                         # if resultstr.find(searchStr) != -1:
#                         #     print '潘雄'
#                         if string.find(resultstr, searchStr) != -1:
#                             print "潘雄"
#                             print sheet.row_values(row)  # 得到row行的所有数据
#                             print "关键字：%s" % sheet.cell_value(row, col).encode('utf-8')
#                             print
#                             print "以下是查询结果："
#                             print "表名: %s" % child.encode('utf-8')
#                             print "sheet名：%s" % sheet.name.encode('utf-8')
#                             print "位置：row = %d, col = %d" % (row + 1, col + 1)
#     end = time.clock()
#     print "查询所花费的时间：%f" % (end - start)


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
