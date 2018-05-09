#!/usr/bin/env python
# coding: utf-8
import os,sys
# 将系统的编码设置为UTF8
os.environ.setdefault("DJANGO_SETTINGS_MODULE","bootcamp2.settings")
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
