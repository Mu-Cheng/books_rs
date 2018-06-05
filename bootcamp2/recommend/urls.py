from django.urls import path

from . import views

urlpatterns = [
    path('', views.recommend, name='recommend'),
    path('update_tag_book', views.update_tag_book, name='update_tag_book'),
    path('update_user_user', views.update_user_user, name='update_user_user'),
    path('update_user_extag', views.update_user_extag, name='update_user_extag'),
    path('update_college_tag', views.update_college_tag, name='update_college_tag'),
    # path('<int:num>/', views.get_stutus, name='get_stutus'),
]
