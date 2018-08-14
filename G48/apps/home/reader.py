# -*- coding: utf-8 -*-
import os
import xlrd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, column_index_from_string
from zipfile import BadZipfile
import unicodecsv as csv
import chardet
import time


def toUnicode(x):
    if not isinstance(x, unicode):
        x = unicode(x)
    return x


def xlsxToUnicode(x):
    y = x.value
    if not isinstance(y, unicode):
        y = unicode(y)
    return y


def read_file_xls(file_name):
    '''
    读取xls表格内容，按照格式返回信息
    '''
    if not os.path.isfile(file_name):
        print '%s不是文件', file_name

    real_file_name = os.path.basename(file_name)       # 得到一个路径下的文件名
    print file_name
    res = {}
    res['tname'] = real_file_name                      # 存储表名
    workbook = xlrd.open_workbook(file_name)
    sheets = workbook.sheets()

    xlsData = {}
    for sheet in sheets:
        sheet_data = {}
        rows = sheet.nrows
        cols = sheet.ncols

        # 有些sheet是空的，防止这种现象
        if rows == 0:
            continue
        sheet_data['sname'] = sheet.name                # 存储sheet名
        sheet_data['content'] = [map(toUnicode, sheet.row_values(row)) for row in range(0, rows)]  # 从第一行开始存储
        sheet_data['header'] = sheet_data['content'][0]
        sheet_data['rows'] = rows
        sheet_data['cols'] = cols
        xlsData[sheet.name] = sheet_data                # 存储数据内容
    res['sheets'] = xlsData                             # 存储所有的sheet
    return res


def read_file_xlsx(file_name):
    '''
    读取xls表格内容，按照格式返回信息
    '''
    if not os.path.isfile(file_name):
        print '%s不是文件', file_name
    print file_name

    real_file_name = os.path.basename(file_name)       # 得到一个路径下的文件名
    res = {}
    res["badFile"] = ""                                # 如果是一个坏文件，则存储
    res['tname'] = real_file_name                      # 存储表名
    sheets = []
    try:
        start = time.clock()
        workbook = load_workbook(file_name)            # 得到一个excel表的对象
        end = time.clock()
        if end - start > 4:
            print "4s:文件:", file_name, "时间：", end-start
            print "**************************"
        sheets = workbook.worksheets                   # 所有的sheet表
    except BadZipfile:
        print "坏文件："
        print file_name
        res["badFile"] = file_name
        return res
    except TypeError:
        print "类型出错文件："
        print file_name
        res["badFile"] = file_name
        return res
    except IOError:
        print "文件损坏文件："
        print file_name
        res["badFile"] = file_name
        return res

    xlsData = {}
    for sheet in sheets:
        sheet_data = {}
        rows = sheet.max_row
        cols = sheet.max_column
        if rows == 0:
            continue
        sheet_data['sname'] = sheet.title                                          # 存储sheet名
        sheet_data['header'] = [i.value for i in list(sheet.rows)[0]]              # 存储表头
        # sheet_data['content'] = [[sheet.cell(row, col).value for col in range(1, cols+1)] for row in range(1, rows+1)]  # 从第一行开始存储
        sheet_data['content'] = [map(xlsxToUnicode, line) for line in list(sheet.rows)]  # 从第一行开始存储

        sheet_data['rows'] = rows
        sheet_data['cols'] = cols
        xlsData[sheet.title] = sheet_data                # 存储数据内容
    res['sheets'] = xlsData                             # 存储所有的sheet
    return res


def read_file_csv(file_name):
    '''
    读取xls表格内容，按照格式返回信息
    '''
    if not os.path.isfile(file_name):
        print '%s不是文件' % file_name
    print file_name

    real_file_name = os.path.basename(file_name)       # 得到一个路径下的文件名
    # 获取文件的编码方式
    csvfile_test_code = open(file_name, 'r')
    file_encoding = chardet.detect(csvfile_test_code.read())  # 获取文件的编码方式
    csvfile_test_code.close()

    # 将GB2312编码改成GBK，以免有中文扩展集导致编码错误
    if file_encoding['encoding'] == "GB2312":
        file_encoding['encoding'] = "GBK"

    res = {}
    xlsData = {}
    res['tname'] = real_file_name                      # 存储表名

    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile, encoding=file_encoding['encoding'])
        try:
            sheet_data = {}
            rows = 0
            cols = 0
            raw_data = [row for row in reader]
            head_row = raw_data[0]                              # 表头数据
            for row in raw_data:                                # 从第一行开始遍历
                # print row
                rows += 1
                if cols < len(row):
                    cols = len(row)
            # print rows, cols
            sheet_data['sname'] = real_file_name  # 存储sheet名
            sheet_data['header'] = head_row       # 存储表头

            for aaa in raw_data:
                for bbb in aaa:
                    if not isinstance(bbb, unicode):
                        print type(bbb), bbb

            content = []
            for line in raw_data:
                line = [s.strip() for s in line]
                if not any(line):
                    continue
                m, n = len(line), cols
                if m < n:
                    line.extend(["" for i in range(n - m)])
                content.append(line)
            sheet_data["content"] = content
            sheet_data['rows'] = rows
            sheet_data['cols'] = cols
            xlsData[real_file_name] = sheet_data  # 存储数据内容
        except UnicodeDecodeError:
            print '编码出错的文件：'
            print file_name
    res['sheets'] = xlsData  # 存储所有的sheet
    return res
