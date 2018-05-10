from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page

import markdown
from bootcamp2.decorators import ajax_required
from bootcamp2.articles.forms import ArticleForm
from bootcamp2.articles.models import Article, Tag, ArticleComment
from bootcamp2.feeds.models import Feed
import redis
import json,pickle

def _articles(request, articles):
    paginator = Paginator(articles, 36)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    popular_tags = Tag.get_popular_tags()
    return render(request, 'articles/articles.html', {'articles': articles, 'popular_tags': popular_tags, 'pages_sum':paginator.num_pages})

# @cache_page(None)
def articles(request):
    all_articles = Article.get_published()
    return _articles(request, all_articles)

# @cache_page(None)
def article(request, slug):
    article = get_object_or_404(Article, slug=slug, status=Article.PUBLISHED)
    # print('type(article.content) : {}'.format(type(article.content)))
    r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=6)
    content = r_db.get(article.title)
    content = str(content, encoding='utf-8')
    content = json.loads(content)
    # print(content)
    book = content['books'][0]
    img = 'http://img-1252422469.file.myqcloud.com/big_bookimg/{}'.format(book['image'].split('/')[-1])
    # print(type(content))
    # print(book['summary'].replace('\n',''))
    con = []
    con.append(['出版社：', book['publisher']])
    con.append(['出版日期：',book['pubdate']])
    con.append(['简介：',book['summary'].replace('\n','')])
    con.append(['目录：',book['catalog'].replace('\n','')])
    con.append(['页数：',book['pages']])
    con.append(['售价：',book['price']])
    ans = {}
    ans['title'] = article.title
    ans['img'] = img
    ans['info'] = con
    # con = '''![{}]({})
    #
    #          1. 出版社：{}\n
    #          2. 出版日期：{}\n
    #          3. 简介:{}\n
    #          4. 目录：{}\n
    #          5. 页数：{}\n
    #          6. 售价：{}\n
    #        '''.format(article.title,
    #                   img,
    #                   book['publisher'],
    #                   book['pubdate'],
    #                   book['summary'].replace('\n',''),
    #                   book['catalog'].replace('\n',''),
    #                   book['pages'],
    #                   book['price'])

    article.content = ans
    return render(request, 'articles/article.html', {'article': article})

# @cache_page(None)
def tag(request, tag_name):
    r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=8)
    r_ans = r_db.get(tag_name)

    if r_ans:
        articles = pickle.loads(r_ans)
    else:
        tags = Tag.objects.filter(tag=tag_name)
        articles = []
        for tag in tags:
            # if tag.article.status == Article.PUBLISHED:
            articles.append(tag.article)
        r_db.setnx(tag_name, pickle.dumps(articles))

    return _articles(request, articles)


@login_required
def write(request):
    if request.method == 'GET':
        form = ArticleForm()
        return render(request, 'articles/write.html', {'form': form})

    form = ArticleForm(request.POST)

    if form.is_valid():
        article = Article()
        article.create_user = request.user
        article.title = form.cleaned_data.get('title')
        article.content = form.cleaned_data.get('content')
        status = form.cleaned_data.get('status')

        if status in [Article.PUBLISHED, Article.DRAFT]:
            article.status = form.cleaned_data.get('status')

        article.save()

        tags = form.cleaned_data.get('tags')
        article.create_tags(tags)

        post = f'{request.user}发布了文章: [{article.title}](https://bootcamp2.herokuapp.com/articles/{article.slug}/)'
        Feed.objects.create(user=request.user, post=post)
        return redirect('/articles/')

    return render(request, 'articles/write.html', {'form': form})


@login_required
def drafts(request):
    drafts = Article.objects.filter(
        create_user=request.user, status=Article.DRAFT)

    return render(request, 'articles/drafts.html', {'drafts': drafts})


@login_required
def edit(request, article_id):
    tags = ''
    if not article_id:
        article = get_object_or_404(Article, pk=article_id)

        for tag in article.get_tags():
            tags = f'{tags} {tag.tag}'
    else:
        article = Article(create_user=request.user)

    if request.POST:
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('/articles/')
    else:
        form = ArticleForm(instance=article, initial={'tags': tags})

    return render(request, 'articles/edit.html', {'form': form})


@login_required
@ajax_required
def preview(request):
    if request.method != 'POST':
        return HttpResponseBadRequest

    content = request.POST.get('content')
    html = _('Nothing to display :(')

    if len(content.strip()) > 0:
        html = markdown.markdown(content, safe_mode='escape')

    return HttpResponse(html)


@login_required
@ajax_required
def comment(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    article_id = request.POST.get('article')
    comment = request.POST.get('comment').strip()

    article = Article.objects.get(pk=article_id)

    if len(comment) > 0:
        ArticleComment.objects.create(
            user=request.user,
            article=article,
            comment=comment
        )

    html = ''
    for comment in article.get_comments():
        template = render_to_string(
            'articles/partial_article_comment.html', {'comment': comment})

        html = f'L{html}{template}'

    return HttpResponse(html)
