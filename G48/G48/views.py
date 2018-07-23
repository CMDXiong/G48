# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
import xlrd
import time
import os



# 每个函数要相隔现个空行
def index(request):
    return HttpResponse("这是一个测试")
    # start = time.clock()
    # filepath = r'F:\Project\G48\导表3'                  # 自动转化成utf-8的字节字符串
    # filepath = filepath.decode('utf-8')                 # 形成无编码的unicode字符集
    # pathDir = os.listdir(filepath)                      # 目录下的所有文件
    #
    # searchStr = u"player_youxia"                        # 查询的字符串（关键字）
    #
    # for allDir in pathDir:
    #     child = os.path.join(filepath, allDir)          # 文件的完整路径
    #     if os.path.isfile(child):                       # 判断路径是不是文件
    #         workbook = xlrd.open_workbook(child)        # excel表
    #         sheets = workbook.sheets()                  # 表中所有sheet
    #         for sheet in sheets:
    #             rows = sheet.nrows                      # sheet对应的行
    #             cols = sheet.ncols                      # sheet对应的列
    #             for row in range(rows):
    #                 for col in range(cols):
    #                     if cmp(sheet.cell_value(row, col), searchStr) == 0:  # 查询row行，col列的值是否与关键字匹配
    #                         print "关键字：%s" % sheet.cell_value(row, col).encode('utf-8')
    #                         print
    #                         print "以下是查询结果："
    #                         print "表名: %s" % child.encode('utf-8')
    #                         print "sheet名：%s" % sheet.name.encode('utf-8')
    #                         print "位置：row = %d, col = %d" % (row + 1, col + 1)
    # end = time.clock()
    #
    # print "查询所花费的时间：%f" % (end - start)
