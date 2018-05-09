#!/usr/bin/python
#  -*- coding:utf-8 -*-

import urllib
import urllib2
import MySQLdb
import sys

URL = "https://api.douban.com/v2/book/search?q="


def main_old():
    reload(sys)                         # 2
    sys.setdefaultencoding('utf-8')
    libData_db = MySQLdb.connect(host="118.89.162.148", port=43306, user="root", passwd="xu695847", db="libData", charset='utf8')
    libData_c = libData_db.cursor()
    libData_c.execute("SELECT * FROM book_key")
    libData_all_data = libData_c.fetchall()

    frist_one = libData_all_data[0]

    bootcamp2_db = MySQLdb.connect(host="118.89.162.148", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()
    str1 = "insert into articles_article(id,title,slug,content,status,create_user_id) values('{}','{}','{}','{}','P','1')".format('3', frist_one[0], '3', frist_one[0])
    # print(str1)
    # ans = bootcamp2_c.execute(str1)
    # print(ans)
    id = 3
    for line in libData_all_data:
        if "'" in line[0]:
            line1 = line[0].replace("'","\\'")
        else:
            line1 = line[0]
        str1 = "insert into articles_article(id,title,slug,content,status,create_user_id) values('{}','{}','{}','{}','P','1');".format(id, line1, id, line1)
        print(str1)
        id = id + 1
        # for item in line:
            # try:
            # print(item)
            # except:
                # pass
    req = urllib2.Request(URL + '《中国现当代文学史》学习辅导与习题集')
    # print(req)

    res_data = urllib2.urlopen(req)
    res = res_data.read()
    # print(res)
    libData_c.close()
    bootcamp2_c.close()

def main():

    reload(sys)                         # 2
    sys.setdefaultencoding('utf-8')
    libData_db = MySQLdb.connect(host="118.89.162.148", port=43306, user="root", passwd="xu695847", db="libData", charset='utf8')
    # libData_c = libData_db.cursor()
    # libData_c.execute("SELECT * FROM model_book_edge")
    # book_db = libData_c.fetchall()
    # books = {}
    # for one in book_db:
    #     key = one[0].encode('utf-8')
    #     print(key)
    #     books[key] = []
    #     for i in range(1, 4):
    #         tem = []
    #         if one[i] == '':
    #             tem.append([])
    #         elif ',' in one[i]:
    #             tem = one[i].split(',')
    #         else:
    #             tem.append(one[i])
    #         # print(type(key))
    #         books[key].append(tem)

        # [one[1], one[2], one[3]]

    # for key, value in books.items():
    #     for book in value:
    #         if book == None:
    #             print('1'*10)
    #         if book == '':
    #             print('2'*10)
    # users = {}


    libData_c = libData_db.cursor()

    bootcamp2_db = MySQLdb.connect(host="118.89.162.148", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()


    libData_c.execute("SELECT * FROM model_borrow_data")
    user_book_db = libData_c.fetchall()
    user_borrow_book = {}
    for one in user_book_db:
        if one[3] in user_borrow_book:
            user_borrow_book[one[3]].append(one[2])
        else:
            user_borrow_book[one[3]] = [one[2]]
    # #
    for key,value in user_borrow_book.items():
        print(key,value)
    id = 8
    # for key, value in user_borrow_book.items():
    #     for book in value:
    #         book = book.encode('utf-8')
    #         # print(type(book))
    #         for i in range(0, 3):
    #             for to_book in books[book][i]:
    #                 print(book, to_book)
    #                 str1 = "insert into feeds_feed(id,post,likes,comments,user_id) values('{}','{}',0,0,{});".format(id, to_book, key)
    #                 id = id + 1
    #                 print(str1)
    #                 bootcamp2_c.execute(str1)
    # #
    #
    #
    # for user in user_db:
    #     users[user_db[0][0]] = []

    # print(type(user_db[0][0]))
    # frist_one = libData_all_data[0]
    #
    # bootcamp2_db = MySQLdb.connect(host="118.89.162.148", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    # bootcamp2_c = bootcamp2_db.cursor()
    # str1 = "insert into articles_article(id,title,slug,content,status,create_user_id) values('{}','{}','{}','{}','P','1')".format('3', frist_one[0], '3', frist_one[0])
    # # print(str1)
    # # ans = bootcamp2_c.execute(str1)
    # # print(ans)
    # id = 3
    # for line in libData_all_data:
    #     if "'" in line[0]:
    #         line1 = line[0].replace("'","\\'")
    #     else:
    #         line1 = line[0]
    #     str1 = "insert into articles_article(id,title,slug,content,status,create_user_id) values('{}','{}','{}','{}','P','1');".format(id, line1, id, line1)
    #     print(str1)
    #     id = id + 1
    #
    #
if __name__ == '__main__':
    main()
