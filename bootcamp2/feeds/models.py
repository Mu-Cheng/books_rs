from django.db import models
import bleach
from django.utils.html import escape
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _  # 延迟翻译
from bootcamp2.activities.models import Activity
from bootcamp2.articles.models import Book as Article
from bootcamp2.articles.models import Tag

from bootcamp2.borrow.models import Borrow

# from bootcamp2.feeds.models import Feed

import markdown
import redis
import json,random
import datetime

STR_NUM = 18

class Feed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    post = models.TextField(max_length=255)
    # parent = models.ForeignKey(
        # 'Feed', null=True, blank=True, on_delete=models.CASCADE)  # 数据库空值保存为NULL，允许输入一个空值
    likes = models.IntegerField(default=0)
    # comments = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def _str_(self):
        return self.post

    @staticmethod
    def get_rand_feeds(from_feed=None):
        return Feed.objects.order_by('?')[:25]


    @staticmethod
    def get_feeds(user_id=None):
        if user_id is not None:
            feeds = Feed.objects.filter(
                user_id=user_id)  # <= gte >=
            # print('get_feeds=', feeds)
        else:

            feeds = Feed.objects.filter()
        return feeds

    @staticmethod
    def get_feeds_after(feed):
        feeds = Feed.objects.filter( id__gt=feed)
        return feeds
    #
    # def get_comments(self):
    #     return Feed.objects.filter(parent=self).order_by('date')
    #
    # def comment(self, user, post):
    #     feed_comment = Feed(user=user, post=post, parent=self)
    #     feed_comment.save()
    #     self.comments = Feed.objects.filter(parent=self).count()
    #     self.save()
    #     return feed_comment

    # def calculate_comments(self):
    #     self.comments = Feed.objects.filter(parent=self).count()
    #     self.save()
    #     return self.comments


    def get_content_len(self):
        end_post = self.post.find(']')
        ans = self.post[1:end_post]
        return len(ans)

    def get_content_has_second(self):
        end_post = self.post.find(']')
        ans = self.post[1:end_post]
        return len(ans) > STR_NUM

    def get_first_p(self):
        tem = self.get_content_as_str()
        if len(tem) > STR_NUM:
            return tem[:STR_NUM]
        else:
            return tem
    def get_second_p(self):
        tem = self.get_content_as_str()
        if len(tem) > STR_NUM:
            return tem[STR_NUM:]
        else:
            return ' '


    def get_content_as_str(self):
        end_post = self.post.find(']')
        ans = self.post[1:end_post]
        return ans

    def get_tags(self):
        return Tag.objects.filter(article_id=self.get_book_id)

    def get_tag_1(self):
        return str(Tag.objects.filter(article_id=self.get_book_id())[0])
    def get_tag_2(self):
        return str(Tag.objects.filter(article_id=self.get_book_id())[1])
    def get_tag_3(self):
        return str(Tag.objects.filter(article_id=self.get_book_id())[2])


    def get_content_as_markdown(self):

        str1 = markdown.markdown(self.post, safe_mode='escape')
        return str1[3:-4]

    def get_img_link(self):
        tem = self.post.split('(')[-1]
        # print(tem.split(')')[-1])
        return tem[:-1]

    def get_book(self):
        # print('get_book',self.post)
        return self.post.split(']')[0][1:]

    def get_book_id(self):
        try:
            ans = self.post.split('/')[-2]
        except:
            ans = ''
        return ans


    def get_img(self):
        r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=6)
        try:
            bookid = self.post.split('/')[-2]
            article = Article.objects.filter(id=bookid)[0]
            content = r_db.get(article.title)
            content = str(content, encoding='utf-8')
            content = json.loads(content)
            # print('{} : {}'.format(article.title,content))
            # for i in range(10):
            #     print('1')

            book = content['books'][0]
            # img = 'http://118.89.162.148/img/{}'.format(book['image'].split('/')[-1])
            img = 'http://img-1252422469.file.myqcloud.com/big_bookimg/{}'.format(book['image'].split('/')[-1])

            # print('article', type(article), article)
            return img
        except:
            return '#'
##
    def calculate_likes(self):
        likes = Activity.objects.filter(
            activity_type=Activity.LIKE, feed=self.pk).count()
        self.likes = likes
        self.save()
        return self.likes

    def get_likes(self):
        likes = Activity.objects.filter(
            activity_type=Activity.LIKE, feed=self.pk)
        return likes

    def get_likers(self):
        likes = self.get_likes()
        likers = []
        for like in likes:
            likers.append(like.user)
        return likers

    def linkfy_post(self):
        return bleach.linkify(escape(self.post))

class Recommend:

    bookid = ''
    book_title = ''

    def __init__(self,bookid='',book_title=''):
        self.bookid = bookid
        self.book_title = book_title

    @staticmethod
    def get_books(user_id=None):
        # print(user_id)
        ans = []
        r_db3 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=3)
        r_db7 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=7)
        r_db2 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=2)
        r_db11 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=11)


        # 获得ItemCF
        item_tags = r_db3.zrevrange(user_id,'0','9')
        for tag in item_tags:
            # print(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))

            book_ids = r_db2.zrevrangebyscore(tag,'+inf','-inf')
            book_tieles = r_db11.mget(book_ids)
            lenth = len(book_ids)
            for i in range(lenth):
                tem = Recommend(str(book_ids[i],encoding='utf-8'),str(book_tieles[i],encoding='utf-8'))
                ans.append(tem)
            # print(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))

        # print(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
        # 获得UserCF
        user_taas = r_db7.zrevrange(user_id,'0','1')
        for tag in user_taas:
            book_ids = r_db2.zrevrangebyscore(tag,'+inf','-inf')
            book_tieles = r_db11.mget(book_ids)
            lenth = len(book_ids)
            for i in range(lenth):
                tem = Recommend(str(book_ids[i],encoding='utf-8'),str(book_tieles[i],encoding='utf-8'))
                ans.append(tem)
        # print(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
        # print(ans)
        random.shuffle(ans)
        # print(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
        # print('*'*60)
        return ans





    def get_img(self):
        r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=6)
        try:

            content = r_db.get(self.book_title)
            content = str(content, encoding='utf-8')
            content = json.loads(content)
            book = content['books'][0]
            img = 'http://img-1252422469.file.myqcloud.com/big_bookimg/{}'.format(book['image'].split('/')[-1])

            return img
        except:
            return '#'
    def get_title(self):
        return self.book_title
    def get_book_id(self):
        # print(self.bookid)
        return self.bookid
    def get_tag_1(self):
        return str(Tag.objects.filter(article_id=self.get_book_id())[0])
    def get_tag_2(self):
        return str(Tag.objects.filter(article_id=self.get_book_id())[1])
    def get_tag_3(self):
        return str(Tag.objects.filter(article_id=self.get_book_id())[2])
