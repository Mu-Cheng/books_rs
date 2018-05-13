from django.contrib import admin
import xadmin
from .models import Borrow

# Register your models here.

@xadmin.sites.register(Borrow)
class BorrowAdmin(object):
    list_display = ("userid", "book_link","img_link","book_name") #界面上展示的列，对应IDC Model的字段
    list_display_links = ("userid",) #带链接可点击的字段，点击会进入编辑界面
