#!/usr/bin/python
#  -*- coding:utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext_lazy as _
from bootcamp2.feeds.models import Feed
from .forms import SignUpForm
from .models import Profile

import redis, pickle

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
    userid = Profile.objects.filter(user=user).values()[0]['user_id']
    # print(userinfo)
    # print(type(userinfo))
    # Profile.objects.filter(user=user)
    # user_list.close()
    in_db5= redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=5)
    out_db= redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=3)
    r_ans = in_db5.get(college)
    tag_codes = pickle.loads(r_ans)
    for tag,code in tag_codes.items():
        out_db.zincrby(userid,tag,amount=code)
    user = authenticate(username=username, password=password)
    login(request, user)

    welcome_post = ('{0}登录了天津理工大学图书推荐系统').format(user.username)
    # Feed.objects.create(user=user, post=welcome_post)

    return redirect('/')
