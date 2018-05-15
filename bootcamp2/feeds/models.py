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
import json

STR_NUM = 18

class Feed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    post = models.TextField(max_length=255)
    parent = models.ForeignKey(
        'Feed', null=True, blank=True, on_delete=models.CASCADE)  # 数据库空值保存为NULL，允许输入一个空值
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)

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
                parent=None, user_id=user_id)  # <= gte >=
            # print('get_feeds=', feeds)
        else:

            feeds = Feed.objects.filter(parent=None)
        return feeds

    @staticmethod
    def get_feeds_after(feed):
        feeds = Feed.objects.filter(parent=None, id__gt=feed)
        return feeds

    def get_comments(self):
        return Feed.objects.filter(parent=self).order_by('date')

    def comment(self, user, post):
        feed_comment = Feed(user=user, post=post, parent=self)
        feed_comment.save()
        self.comments = Feed.objects.filter(parent=self).count()
        self.save()
        return feed_comment

    def calculate_comments(self):
        self.comments = Feed.objects.filter(parent=self).count()
        self.save()
        return self.comments


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
