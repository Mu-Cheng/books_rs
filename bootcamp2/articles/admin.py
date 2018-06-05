# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import loader
from xadmin.views import BaseAdminPlugin, ListAdminView,CommAdminView
from django.contrib import admin
import xadmin


from .models import Book , Tag, ArticleComment
from xadmin import views
@xadmin.sites.register(views.website.IndexView)
class MainDashboard(object):
    widgets = [
        [
            {"type": "html", "title": "Test Widget",
             "content": "<h3> Welcome to Xadmin! </h3><p>Join Online Group: <br/>QQ Qun : 282936295</p>"},
            {"type": "chart", "model": "app.accessrecord", "chart": "user_count",
             "params": {"_p_date__gte": "2013-01-08", "p": 1, "_p_date__lt": "2013-01-29"}},
            {"type": "list", "model": "app.host", "params": {"o": "-guarantee_date"}},
        ],
        [
            {"type": "qbutton", "title": "Quick Start",
             "btns": [{"model": Book}, {"model": Tag}, {"title": "Google", "url": "http://www.google.com"}]},
            {"type": "addform", "model": ArticleComment},
        ]
    ]
#
# class RsPlugin(BaseAdminPlugin):
#     demo_plugin = False
#
#     def init_request(self, *args, **kwargs):
#         return self.demo_plugin
#
#     def block_top_toolbar(self, context, nodes):
#         if self.demo_plugin:
#             content = 'Python + Django + xadmin 快速开发教程'
#             # context.render({
#             #     'about_content': content
#             #     })
#             context.update({
#                 'about_content': content
#                 })
#         print(context)
#         print(type(context))
#         nodes.append(
#             loader.render_to_string('articles/plugin.html',
#                             context)
#         )
# xadmin.site.register_plugin(RsPlugin, CommAdminView)

# 基本的修改
class BaseSetting(object):
    enable_themes = True   # 打开主题功能
    use_bootswatch = True  #

# 针对全局的
class GlobalSettings(object):
    site_title = "TJUT图书推荐系统后台管理系统"  # 系统名称
    site_footer = "TJUT"      # 底部版权栏
    # menu_style = "accordion"     # 将菜单栏收起来

xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)

@xadmin.sites.register(Book)
class ArticleAdmin(object):
    list_display = ("slug","title", "img_name", "author", "publisher","pubdate","summary","catalog","pages","price") #界面上展示的列，对应IDC Model的字段
    list_display_links = ("title",) #带链接可点击的字段，点击会进入编辑界面
    demo_plugin = True

# @xadmin.sites.register(Tag)
# class TagAdmin(object):
#     list_display = ("article", "tag") #界面上展示的列，对应IDC Model的字段
#     list_display_links = ("article",) #带链接可点击的字段，点击会进入编辑界面
# @xadmin.sites.register(Article)
# class ArticleCommentAdmin(object):
#     list_display = ("article", "comment", "date", "user") #界面上展示的列，对应IDC Model的字段
#     list_display_links = ("tiarticletle",) #带链接可点击的字段，点击会进入编辑界面
xadmin.site.register(Tag)
xadmin.site.register(ArticleComment)


# xadmin.sites.register(RsPlugin)
