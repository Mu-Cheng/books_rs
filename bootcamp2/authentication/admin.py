 # -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Profile
# from bootcamp2 import xadmin
# from bootcamp2.xadmin import views

import xadmin
from xadmin.sites import site
from xadmin import views
from xadmin.views import BaseAdminPlugin, ListAdminView

# admin.site.register(Profile)
@xadmin.sites.register(Profile)
class UserAdmin(object):
    list_display = ("student_number","name", "college", "identity", "picture_url") #界面上展示的列，对应IDC Model的字段
    list_display_links = ("student_number",) #带链接可点击的字段，点击会进入编辑界面
