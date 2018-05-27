#!/usr/bin/python
#  -*- coding:utf-8 -*-

import MySQLdb
import csv
# import requests
import redis
import time,json
import math,pickle
from tqdm import tqdm

def update_tag_book():
    bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()
    bootcamp2_c.execute('select * from articles_tag')

    r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=2)
    tag_books = bootcamp2_c.fetchall()
    sum = len(tag_books)
    pos = 1
    for tag_book in tag_books:
        print('{}/{}'.format(pos,sum))
        r_db.lpush(tag_book[1],tag_book[2])
        pos = pos + 1


    bootcamp2_c.close()
    bootcamp2_db.close()

def update_user_tag():
    r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=3)
    anss = r_db.zrevrangebyscore('5141','+inf','-inf')
    for ans in anss:
        ans = str(ans, encoding='utf-8')
        score = r_db.zscore('5141',ans)
        print(ans,score)
        return 0
        bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
        bootcamp2_c = bootcamp2_db.cursor()
        bootcamp2_c.execute('SELECT borrow_borrow.userid,articles_tag.tag FROM borrow_borrow,articles_book,articles_tag WHERE borrow_borrow.book_name=articles_book.title AND articles_book.id = articles_tag.article_id')
        user_tags = bootcamp2_c.fetchall()

        sum = len(user_tags)
        pos = 1
        for user_tag in user_tags:
            print('{}/{}'.format(pos,sum))
            r_db.zincrby(user_tag[0],user_tag[1],amount=1)
            pos = pos + 1


            bootcamp2_c.close()
            bootcamp2_db.close()

def get_juli(a,b):
    return (a-b)*(a-b)

def get_score(list_1,list_2):
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

def update_user_user():
    in_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=3)
    out_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=4)
    keys = in_db.keys()
    user_user = {}
    sum = len(keys)
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

    pos = 0
    for i in range(sum):
        for j in range(i+1,sum):

            ans = get_score(user_user[i],user_user[j])

            if ans != 0 and ans > 2:
                out_db.zincrby(keys[i],keys[j],amount=ans)
                out_db.zincrby(keys[j],keys[i],amount=ans)

                print(keys[i],keys[j],ans)
        pos = pos + 1
        print("{}/{}".format(pos,sum))

def update_user_user():
    in_db3 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=3)
    in_db4 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=4)
    out_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=7)
    keys = in_db3.keys()
    user_user = {}
    sum = len(keys)
    for i in range(sum):
        anss = in_db4.zrevrange(keys[i],'0','99')
        key = str(keys[i], encoding='utf-8')
        user_user[key] = anss
    sum = len(user_user)
    pos = 1
    for key,val_list in user_user.items():
        print(key)
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
        print('{}/{}'.format(pos,sum))
        pos = pos + 1


def update_db2():
    bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()
    bootcamp2_c.execute('select * from articles_tag')

    out_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=2)
    tag_books = bootcamp2_c.fetchall()
    sum = len(tag_books)
    pos = 1
    book_tags = {}

    bootcamp2_c.execute('SELECT slug,title FROM articles_book')
    id_titledbs = bootcamp2_c.fetchall()
    id_titles = {}
    for it in id_titledbs:
        id_titles[str(it[0])] = it[1]

    for tag_book in tag_books:
        print('{}/{}'.format(pos,sum))
        # print(type(tag_book[2]))
        # print(tag_book[2])

        try:
            book_tags[str(tag_book[2])]
        except:
            book_tags[str(tag_book[2])] = []
        book_tags[str(tag_book[2])].append(tag_book[1])
        out_db.zincrby(tag_book[1],tag_book[2],amount=1)
        # r_db.lpush(tag_book[1],tag_book[2])
        pos = pos + 1
    print("*"*60)
    bootcamp2_c.execute('SELECT articles_book.slug FROM articles_book,borrow_borrow WHERE articles_book.title=borrow_borrow.book_name')

    books = bootcamp2_c.fetchall()
    print("*"*60)

    sum = len(books)
    print(sum)
    pos = 1
    for book in books:
        book = book[0]
        # try:
        #     title = book[1]
        # except:
        #     continue
        try:
            book_tags[book]
        except:
            # print(type(book))
            # print(book)
            print('E {}/{}'.format(pos,sum))
            pos = pos + 1
            continue
        for tag in book_tags[book]:
            out_db.zincrby(tag,book,amount=1)
        print('{}/{}'.format(pos,sum))
        pos = pos + 1

    bootcamp2_c.close()
    bootcamp2_db.close()

def update_db11():
    bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()
    out_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=11)
    bootcamp2_c.execute('SELECT slug,title FROM articles_book')
    id_titledbs = bootcamp2_c.fetchall()
    id_titles = {}
    for it in id_titledbs:
        out_db.set(it[0],it[1])
        # id_titles[str(it[0])] = it[1]
def update_db5():
    bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()
    bootcamp2_c.execute('SELECT user_id,college FROM authentication_profile')
    id_colleges = bootcamp2_c.fetchall()
    ans = {}
    in_db3 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=3)
    out_db3 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=5)
    for id_college in tqdm(id_colleges):
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

    for college,tags in tqdm(ans.items()):
        college = college[0]
        sorts=sorted(tags.items(),key=lambda e:e[1],reverse=True)
        cnt = 0
        tem = {}
        for it in sorts:
            tem[it[0]] = it[1]
            cnt = cnt + 1
            if cnt >= 10:
                break
        out_db3.setnx(college, pickle.dumps(tem))



    bootcamp2_c.close()
    bootcamp2_db.close()
def main():
    out_db3 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=5)
    keys = out_db3.keys()
    ans = '['
    for key in keys:
        ans = ans + "('{}','{}'),".format(str(key, encoding='utf-8'),str(key, encoding='utf-8'))
    ans= ans+'],'
    print(ans)
if __name__ =='__main__':
    main()
