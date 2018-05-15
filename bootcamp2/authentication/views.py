#!/usr/bin/python
#  -*- coding:utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext_lazy as _
from bootcamp2.feeds.models import Feed
from .forms import SignUpForm
from .models import Profile


# is_valid是否合法, cleaned_data 清理格式
def signup(request):
    # 展示注册界面
    if request.method != 'POST':
        return render(request, 'auth/signup.html', {'form': SignUpForm()})
    # 添加用户
    form = SignUpForm(request.POST)

    if not form.is_valid():
        return render(request, 'auth/signup.html', {'form': form})

    email = form.cleaned_data.get('email')
    username = form.cleaned_data.get('username')
    password = form.cleaned_data.get('password')
    college = form.cleaned_data.get('college')
    identity = form.cleaned_data.get('identity')
    # print(identity)
    user = User.objects.create_user(
        username=username, password=password, email=email
        )
    Profile.objects.filter(user=user).update(college=college,identity=identity)
    # user_list.close()
    user = authenticate(username=username, password=password)
    login(request, user)

    welcome_post = ('{0}登录了天津理工大学图书推荐系统').format(user.username)
    # Feed.objects.create(user=user, post=welcome_post)

    return redirect('/')
