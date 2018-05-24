from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
import markdown,redis,json,pickle, random


# choice 最好在模型内部定义，然后给每个值定义一个合适名字的常量，方便外部引用
# on_delete 删除联级, related_name 不创建反向关联
class Book(models.Model):
    DRAFT = 'D'
    PUBLISHED = 'P'
    STATUS = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    img_name = models.SlugField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    pubdate = models.CharField(max_length=255, blank=True, null=True)
    summary =  models.TextField(max_length=4000, blank=True, null=True)
    catalog = models.TextField(max_length=4000, blank=True, null=True)
    pages = models.CharField(max_length=255, blank=True, null=True)
    price = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    create_user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)
    update_user = models.ForeignKey(
        User, blank=True, null=True, related_name='+', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-create_date',)

    def __str__(self):
        return self.title

    def save(self, *args, **kw):
        if not self.pk:
            super(Book, self).save(*args, **kw)
        else:
            self.update_date = datetime.now()
        if not self.slug:
            slug_str = f'{self.pk}{self.title.lower()}'
            self.slug = slugify(slug_str)
        super(Book, self).save(*args, **kw)

    def get_content_as_markdown(self):
        return markdown.markdown(self.content, safe_mode='escape')

    def get_img(self):
        r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=6)
        try:
            # bookid = self.post.split('/')[-2]
            # article = Article.objects.filter(id=self.slug)[0]
            # print('title :{}'.format(self.title))
            content = r_db.get(self.title)
            content = str(content, encoding='utf-8')
            content = json.loads(content)

            book = content['books'][0]
            # img = 'http://118.89.162.148/img/{}'.format(book['image'].split('/')[-1])
            img = 'http://img-1252422469.file.myqcloud.com/big_bookimg/{}'.format(book['image'].split('/')[-1])
            # img = 'http://118.89.162.148/img/{}'.format(book['image'].split('/')[-1])

            # print('article', type(article), article)
            return img
        except:
            return '#'

    # def get_content(self):

    @staticmethod
    def get_published():
        articles = Book.objects.filter(status=Book.PUBLISHED)
        return articles

    @staticmethod
    def get_colour():
        colours = [
            'default',
            'primary',
            'success',
            'info',
            'warning',
            'danger',
        ]
        pos = random.randint(0,5)
        colour = colours[pos]
        # print(colour)
        return colour


    def create_tags(self, tags):
        tags = tags.strip()
        tag_list = tags.split(' ')
        for tag in tag_list:
            if tag:
                t, created = Tag.objects.get_or_create(
                    tag=tag.lower(), article=self)

    def get_tags(self):
        return Tag.objects.filter(article=self)

    def get_summary(self):
        if len(self.content) > 255:
            return f'{self.content[:255]}...'
        else:
            return self.content

    def get_summary_as_markdown(self):
        return markdown.markdown(self.get_summary(), safe_mode='escape')

    def get_comments(self):
        return ArticleComment.objects.filter(article=self)

# 设置不重复的字段组合， 设置带有索引的字段组合


class Tag(models.Model):
    tag = models.CharField(max_length=50)
    article = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('tag', 'article'),)
        index_together = [['tag', 'article'], ]

    def __str__(self):
        return self.tag

    @staticmethod
    def get_popular_tags():
        r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=1)
        r_ans = r_db.get('tags')
        if r_ans:
            sorted_count = pickle.loads(r_ans)
            return sorted_count[:50]
        else:
            count = {}
            all_tag = Tag.objects.all()
            for tag in all_tag:
                # if tag.article.status != Article.PUBLISHED:
                    # continue
                if tag.tag in count:
                    count[tag.tag] += 1
                else:
                    count[tag.tag] = 1
            sorted_count = sorted(list(count.items()),
                                  key=lambda t: t[1], reverse=True)
            r_db.setnx('tags', pickle.dumps(sorted_count))
            result = sorted_count[:50]
            # print('result : {}'.format(result))
            # print('type : {}'.format(type(result)))
            # r_db.rpush('tags',)
            return result


class ArticleComment(models.Model):
    article = models.ForeignKey(Book, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('date',)

    def __str__(self):
        return f'{self.user.username} {self.article.title}'
