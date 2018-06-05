from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import MySQLdb
import csv
# import requests
import redis
import time,json
import math,pickle
from tqdm import tqdm
from bootcamp2.public import get_redis_connction
import threading
from bootcamp2.public import get_redis_connction
# from bootcamp2.consumers import RecommendStutus
from channels import layers
from bootcamp2.settings import CHANNEL_LAYERS
from asgiref.sync import async_to_sync

# from rest_framework import serializers

# Create your views here.

def get_stutus(request, num,type=False):

    if not request.user.is_superuser:
        return render(request, '404.html')
    out_db9 = get_redis_connction(db=9)
    try:
        status = pickle.loads(out_db9.get(num))
    except:
        status = {
            'open':False
        }
    if type:
        return status
    else:
        return HttpResponse(json.dumps(status))

def recommend(request):
    if request.user.is_superuser:
        return render(request, 'recommend/recommend.html',{
            'status2' : get_stutus(request,2,True),
            'status4' : get_stutus(request,4,True),
            'status7' : get_stutus(request,7,True),
            'status5' : get_stutus(request,5,True),
        })
    else:
        return render(request, '404.html')

def _opt_db(db,func):


    out_db9 = get_redis_connction( db=9)
    try:
        status = pickle.loads(out_db9.get(db))
        if status['open'] :
            return redirect('/recommend')
    except:
        pass
    t = threading.Thread(target=func, daemon=True)
    t.start()
    # return redirect('/recommend')
    return HttpResponseRedirect('/recommend')

def update_tag_book(request):
    if not request.user.is_superuser:
        return render(request, '404.html')
    return _opt_db(2,_update_db2)

def update_user_user(request):
    if not request.user.is_superuser:
        return render(request, '404.html')
    return _opt_db(4,_update_db4)

def update_user_extag(request):
    if not request.user.is_superuser:
        return render(request, '404.html')
    return _opt_db(7,_update_db7)

def update_college_tag(request):
    if not request.user.is_superuser:
        return render(request, '404.html')
    return _opt_db(5,_update_db5)

def _send_group(channel_layer,status):
    async_to_sync(channel_layer.group_send)(
            "rs_loging",
            {
                "type": "chat.message",
                "text": json.dumps(status)
            },
        )

def _update_db5():
    bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()
    bootcamp2_c.execute('SELECT user_id,college FROM authentication_profile')
    id_colleges = bootcamp2_c.fetchall()
    ans = {}
    out_db9 = get_redis_connction( db=9)
    status = {
        'open' : True,
        'length' : 0
    }
    out_db9.set(5, pickle.dumps(status))
    in_db3 = get_redis_connction( db=3)
    out_db5 = get_redis_connction( db=5)
    out_db5.flushdb()
    channel_layer =  layers.get_channel_layer()
    status['open'] = 'db5'
    _send_group(channel_layer,status)
    sum = len(id_colleges)
    pos = 1
    old_num = -1
    for id_college in id_colleges:
        id = str(id_college[0])
        if  id_college[1] is None or id_college[1] == '' or id_college[1].isspace():
            continue
        college = id_college[1],
        try:
            ans[college]
        except:
            ans[college] = {}
        tags = in_db3.zrevrangebyscore(id,'+inf','-inf',withscores=True)
        for tag_code in tags:
            tag = str(tag_code[0], encoding='utf-8')
            code = tag_code[1]
            try:
                ans[college][tag]
            except:
                ans[college][tag] = 0
            ans[college][tag] = ans[college][tag] + code
        new_num =  pos*100//sum
        if old_num != new_num:
            status['progress1'] =new_num
            _send_group(channel_layer,status)
            old_num = new_num
        pos = pos + 1
    status['progress1'] =100
    _send_group(channel_layer,status)
    sum = len(ans)
    old_num = -1
    pos = 1
    for college,tags in ans.items():
        college = college[0]
        sorts=sorted(tags.items(),key=lambda e:e[1],reverse=True)
        cnt = 0
        tem = {}
        for it in sorts:
            tem[it[0]] = it[1]
            cnt = cnt + 1
            if cnt >= 10:
                break
        # out_db5.setnx(college, pickle.dumps(tem))
        new_num =  pos*100//sum
        if old_num != new_num:
            status['progress2'] =new_num
            _send_group(channel_layer,status)
            old_num = new_num
        pos = pos + 1
    status['progress2'] =100
    _send_group(channel_layer,status)
    status['open'] = False
    status['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    out_db9.set(5, pickle.dumps(status))

def _update_db7():
    out_db9 = get_redis_connction( db=9)
    status = {
        'open' : True,
        'length' : 0
    }
    out_db9.set(7, pickle.dumps(status))
    channel_layer =  layers.get_channel_layer()
    status['open'] = 'db7'
    _send_group(channel_layer,status)

    in_db3 = get_redis_connction( db=3)
    in_db4 = get_redis_connction( db=4)
    out_db = get_redis_connction( db=7)
    out_db.flushdb()

    keys = in_db3.keys()
    user_user = {}
    sum = len(keys)
    for i in range(sum):
        anss = in_db4.zrevrange(keys[i],'0','99')
        key = str(keys[i], encoding='utf-8')
        user_user[key] = anss
    sum = len(user_user)
    pos = 1
    status['progress1'] = 0
    # out_db9.set(7, pickle.dumps(status))
    old_num=-1
    for key,val_list in user_user.items():
        # print(key)
        user_tag_db3 = in_db3.zrevrangebyscore(key,'+inf','-inf')
        new_tag_set = set()
        tag_code = {}
        for to_user in val_list:
            anss = in_db3.zrevrange(to_user,'0','39',withscores=True)
            for ans in anss:
                try:
                    tag_code[ans[0]]
                except:
                    tag_code[ans[0]] = 0
                tag_code[ans[0]] = tag_code[ans[0]] + ans[1]
                new_tag_set.add(ans[0])
        old_tag_set = set(user_tag_db3)
        ex_tags = new_tag_set - old_tag_set
        tem = {}
        for tag in ex_tags:
            tem[str(tag,encoding='utf-8')] = tag_code[tag]
        sorts=sorted(tem.items(),key=lambda e:e[1],reverse=True)

        cnt = 0
        for sort_ans in sorts:
            out_db.zincrby(key,sort_ans[0],amount=sort_ans[1])
            cnt = cnt + 1
            if cnt >= 100:
                break
        # print('{}/{}'.format(pos,sum))
        new_num =  pos*100//sum
        if old_num != new_num:
            status['progress1'] =new_num
            _send_group(channel_layer,status)
            old_num = new_num

        # out_db9.set(7, pickle.dumps(status))
        pos = pos + 1

    status['progress1'] = 100
    _send_group(channel_layer,status)

    status['open'] = False
    status['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    out_db9.set(7, pickle.dumps(status))

def _get_score(list_1,list_2):
    sum = 0
    # cnt = 0
    for key,val in list_1.items():
        if key in list_2:
            # print('*'*40)
            # print(type(val))
            # print(type(list_2[key]))
            # print(min(val,list_2[key]))
            # print('*'*40)

            sum = sum + min(val,list_2[key])

    return sum


def _update_db4():
    out_db9 = get_redis_connction( db=9)
    status = {
        'open' : True,
        'length' : 0
    }
    out_db9.set(4, pickle.dumps(status))
    channel_layer =  layers.get_channel_layer()
    status['open'] = 'db4'
    _send_group(channel_layer,status)

    in_db = get_redis_connction( db=3)
    out_db = get_redis_connction( db=4)
    out_db.flushdb()
    keys = in_db.keys()
    user_user = {}
    sum = len(keys)
    pos = 1
    status['progress1'] = 0
    old_num = -1
    for i in range(sum):
        key = keys[i]
        anss = in_db.zrevrangebyscore(key,'+inf','-inf')
        for ans in anss:
            ans = str(ans, encoding='utf-8')
            score = in_db.zscore(key,ans)
            try:
                user_user[i]
            except:
                user_user[i] = {}
            user_user[i][ans] = score
            # print(ans,score)
        new_num =  pos*100//sum
        if old_num != new_num:
            status['progress1'] =new_num
            _send_group(channel_layer,status)
            old_num = new_num

        # out_db9.set(4, pickle.dumps(status))
        pos = pos + 1
    status['progress1'] = 100
    _send_group(channel_layer,status)

    # out_db9.set(4, pickle.dumps(status))
    pos = 0
    status['progress2'] = 0
    old_num = -1
    for i in range(sum):
        for j in range(i+1,sum):

            ans = _get_score(user_user[i],user_user[j])

            if ans != 0 and ans > 2:
                out_db.zincrby(keys[i],keys[j],amount=ans)
                out_db.zincrby(keys[j],keys[i],amount=ans)

                # print(keys[i],keys[j],ans)
        pos = pos + 1
        new_num =  pos*100//sum
        if old_num != new_num:
            status['progress2'] =new_num
            _send_group(channel_layer,status)
            old_num = new_num

        # out_db9.set(4, pickle.dumps(status))
        # print(pos,sum)
    status['progress2'] = 100
    _send_group(channel_layer,status)

    status['open'] = False
    status['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    out_db9.set(4, pickle.dumps(status))

        # print("{}/{}".format(pos,sum))


def _update_db2():
    bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()
    bootcamp2_c.execute('select * from articles_tag')

    out_db = get_redis_connction( db=2)
    out_db.flushdb()
    out_db9 = get_redis_connction( db=9)
    # recommendStutus = RecommendStutus()
    channel_layer =  layers.get_channel_layer()
    status = {
        'open' : True
        # 'length' : 0
    }

    out_db9.set(2, pickle.dumps(status))
    status['open'] = 'db2'
    status['progress1'] = 0
    status['progress2'] = 0
    async_to_sync(channel_layer.group_send)(
            "rs_loging",
            {
                "type": "chat.message",
                "text": json.dumps(status)
            },
        )

    tag_books = bootcamp2_c.fetchall()
    sum = len(tag_books)
    pos = 1
    book_tags = {}

    bootcamp2_c.execute('SELECT slug,title FROM articles_book')
    id_titledbs = bootcamp2_c.fetchall()
    id_titles = {}

    for it in id_titledbs:
        id_titles[str(it[0])] = it[1]

    # out_db9.set(2, pickle.dumps(status))
    old_num = -1
    for tag_book in tag_books:
        new_num = pos*100//sum
        if old_num != new_num:
            status['progress1'] = new_num
            async_to_sync(channel_layer.group_send)(
                    "rs_loging",
                    {
                        "type": "chat.message",
                        "text": json.dumps(status)
                    },
                )
            old_num=new_num

        try:
            book_tags[str(tag_book[2])]
        except:
            book_tags[str(tag_book[2])] = []
        book_tags[str(tag_book[2])].append(tag_book[1])
        out_db.zincrby(tag_book[1],tag_book[2],amount=1)

        pos = pos + 1
    status['progress1'] = 100
    async_to_sync(channel_layer.group_send)(
            "rs_loging",
            {
                "type": "chat.message",
                "text": json.dumps(status)
            },
        )

    bootcamp2_c.execute('SELECT articles_book.slug FROM articles_book,borrow_borrow WHERE articles_book.title=borrow_borrow.book_name')

    books = bootcamp2_c.fetchall()

    sum2 = len(books)
    pos = 1
    old_num = -1
    for book in books:
        book = book[0]
        try:
            book_tags[book]
        except:
            pos = pos + 1
            continue
        for tag in book_tags[book]:
            out_db.zincrby(tag,book,amount=1)
        new_num = pos*100//sum2
        if old_num != new_num:
            status['progress2'] = new_num
            async_to_sync(channel_layer.group_send)(
                    "rs_loging",
                    {
                        "type": "chat.message",
                        "text": json.dumps(status)
                    },
                )
            old_num=new_num
        pos = pos + 1
    status['progress2'] = 100
    async_to_sync(channel_layer.group_send)(
            "rs_loging",
            {
                "type": "chat.message",
                "text": json.dumps(status)
            },
        )
    status['open'] = False
    status['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    out_db9.set(2, pickle.dumps(status))
    bootcamp2_c.close()
    bootcamp2_db.close()
