from django.contrib import admin
import xadmin


from .models import Feed

# admin.site.register(Feed)
@xadmin.sites.register(Feed)
class FeedAdmin(object):
    list_display = ("user", "post") #界面上展示的列，对应IDC Model的字段
    list_display_links = ("user",) #带链接可点击的字段，点击会进入编辑界面
