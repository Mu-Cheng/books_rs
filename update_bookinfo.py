#!/usr/bin/python
#  -*- coding:utf-8 -*-

import MySQLdb
import csv
# import requests
import redis
import time,json


def main():
    bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()
    bootcamp2_c.execute('select title from articles_book')

    titles = bootcamp2_c.fetchall()
    sum = len(titles)
    pos = 1
    for title in titles:
        r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=6)
        content = r_db.get(title[0])
        try:
            content = str(content, encoding='utf-8')
        except:
            continue
        content = json.loads(content)
        # print(content)
        try:
            book = content['books'][0]
        except:
            continue
        con = {'img_name':book['image'].split('/')[-1]}
        con['author'] = ''
        for author in book['author']:
            con['author'] = con['author'] + author + " "
        # str(book['author'])[2:-2]
        con['author'] = con['author'].replace('"','\\"').replace("'","\\'")
        con['publisher'] = book['publisher'].replace('"','\\"').replace("'","\\'")
        con['pubdate'] = book['pubdate'].replace('"','\\"').replace("'","\\'")
        con['summary'] = book['summary'].replace('"','\\"').replace("'","\\'")
        con['catalog'] = book['catalog'].replace('"','\\"').replace("'","\\'")
        con['pages']  = book['pages'].replace('"','\\"').replace("'","\\'")
        con['price'] = book['price'].replace('"','\\"').replace("'","\\'")

        str1 = 'update articles_book set '
        ok = 1
        for key,val in con.items():
            if ok == 1:
                str1 = str1 + "{}='{}'".format(key,val)
                ok = 0
            else:
                str1 = str1 + ',' + "{}='{}'".format(key,val)
        str1 = str1 + ' where title="{}"'.format(title[0].replace('"','\\"').replace("'","\\'"))
        # print(str1)
        print('{} {}/{}'.format(title[0].replace('"','\\"').replace("'","\\'"),pos,sum))
        pos = pos + 1
        bootcamp2_c.execute(str1)
        bootcamp2_db.commit()
        # print(title)

    bootcamp2_c.close()
    bootcamp2_db.close()
if __name__ =='__main__':
    main()
