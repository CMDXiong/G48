# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

app_name = 'home'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search_result/', views.search_result, name='search_result'),
    url(r'^config/$', views.config, name='config'),
    url(r'^common/auth.html$', views.config, name='config'),

]
