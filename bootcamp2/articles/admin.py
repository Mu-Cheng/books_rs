from django.contrib import admin
import xadmin


from .models import Book , Tag, ArticleComment
from xadmin import views

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
