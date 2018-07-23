# -*- coding: utf-8 -*-
from django import template

register = template.Library()


def get_child_list(lists, num):
    return lists[num]


def greet(value, word):
    return value+word


register.filter("get_child_list", get_child_list)
register.filter("greet", greet)
