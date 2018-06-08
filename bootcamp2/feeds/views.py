from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from django.views.decorators.gzip import gzip_page
from django.views.decorators.cache import cache_page

from bootcamp2.decorators import ajax_required
from bootcamp2.articles.models import Book as Article,Tag
from bootcamp2.articles.views import tag
from bootcamp2.borrow.models import Borrow
from bootcamp2.public import get_redis_connction





from .models import Feed,Recommend
import redis, time, pickle,MySQLdb,json,random,datetime,tqdm

FEEDS_NUM_PATES = 24
NO_USER = 'AnonymousUser'
# @cache_page(None)
@gzip_page
def feeds(request):
    user = request.user
    user = '{}'.format(user)
    if user == NO_USER:
        return render(request, 'feeds/nouser_home.html', {
        })

    r_db = get_redis_connction(8)
    r_ans = r_db.get(user)
    bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()
    bootcamp2_c.execute('select id from auth_user where username = \'{}\''.format(user))
    user_id = bootcamp2_c.fetchone()
    user_id = user_id[0]
    bootcamp2_c.close()
    bootcamp2_db.close()
    if r_ans:
        paginator = pickle.loads(r_ans)
    else:
        try:
            all_feeds = Recommend.get_books(user_id)
        except:
            all_feeds = Recommend.get_books(3)
        paginator = Paginator(all_feeds, FEEDS_NUM_PATES)
        if paginator.num_pages < 2:
            return tag(request,'小说')
        r_db.setnx(user, pickle.dumps(paginator))


    page = request.GET.get('page')

    try:
        page = random.randint(1,paginator.num_pages-1)
        feeds = paginator.page(page)
    except PageNotAnInteger:
        feeds = paginator.page(1)
    except EmptyPage:
        feeds = paginator.page(paginator.num_pages)
    return render(request, 'feeds/feeds.html', {
        'feeds': feeds,
        'borrow_sum': Borrow.get_borrowed_sum(user_id),
        'page': 1,
    })

# @cache_page(None)
@gzip_page
def borrowed(request):
    user = request.user
    user_id = None
    if user == NO_USER:
        return render(request, 'feeds/borrowed_feeds.html', {
            'borrows': None,
            'page': 1,
        })

    if request.POST:
        mode = request.POST['mode']
        book_name = request.POST['book_name']
        book_id = request.POST['book_id']



        book_link = 'http://118.89.162.148/articles/{}'.format(request.POST['book_id'])
        r_db = get_redis_connction(6)
        print(book_name)
        content = r_db.get(book_name)
        content = str(content, encoding='utf-8')
        content = json.loads(content)
        book = content['books'][0]
        img_link = book['image'].split('/')[-1]

        bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
        bootcamp2_c = bootcamp2_db.cursor()
        bootcamp2_c.execute('select id from auth_user where username = \'{}\''.format(user))
        user_id = bootcamp2_c.fetchone()
        userid = user_id[0]
        user_id = userid


        bootcamp2_c.close()
        bootcamp2_db.close()
        if mode == 'borrow_book':
            Borrow.objects.create(userid = userid,
                                  book_link = book_link,
                                  img_link = img_link,
                                  book_name = book_name)

            r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=10)
            try:
                r_db.delete(user)
            except:
                pass
            r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=8)
            try:
                r_db.delete(user)
            except:
                pass
            tags = Tag.objects.filter(article_id=book_id)
            r_db3 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=3)
            for tag in tags:
                r_db3.zincrby(user_id,tag,amount=1)
        if mode == 'return_book':
            try:
                Borrow.objects.filter(userid = userid,
                                      book_link = book_link,
                                      img_link = img_link,
                                      book_name = book_name).delete()
                r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=10)
                try:
                    r_db.delete(user)
                except:
                    pass
                tags = Tag.objects.filter(article_id=book_id)
                r_db3 = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=3)
                for tag in tags:
                    r_db3.zincrby(user_id,tag,amount=-0.5)
            except:
                print('return book {} fail'.format(book_name))
    else:
        userid = None

    r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=10)
    r_ans = r_db.get(user)
    if r_ans:
        paginator = pickle.loads(r_ans)
    else:
        if userid is None:
            bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
            bootcamp2_c = bootcamp2_db.cursor()
            bootcamp2_c.execute('select id from auth_user where username = \'{}\''.format(user))
            user_id = bootcamp2_c.fetchone()
            userid = user_id[0]
            user_id = userid
            bootcamp2_c.close()
            bootcamp2_db.close()

        all_borrowed = Borrow.get_borrowed(userid)
        paginator = Paginator(all_borrowed, FEEDS_NUM_PATES)

        r_db.setnx(user, pickle.dumps(paginator))

    borrows = paginator.page(1)
    from_feed = -1
    if borrows:
        from_feed = borrows[0].id

    if user_id is None:
        bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
        bootcamp2_c = bootcamp2_db.cursor()
        bootcamp2_c.execute('select id from auth_user where username = \'{}\''.format(user))
        user_id = bootcamp2_c.fetchone()
        user_id = user_id[0]
        bootcamp2_c.close()
        bootcamp2_db.close()
    return render(request, 'feeds/borrowed_feeds.html', {
        'borrows': borrows,
        'borrow_sum' : Borrow.get_borrowed_sum(user_id),
        'page': 1,
        'pages_sum': paginator.num_pages,
    })



def feed(request, pk):
    localtime = time.asctime(time.localtime(time.time()))
    feed = get_object_or_404(Feed, pk=pk)
    localtime = time.asctime(time.localtime(time.time()))
    return render(request, 'feeds/feed.html', {'feed': feed})


@ajax_required
def load(request):
    user = request.user
    page = request.GET.get('page')
    from_feed = request.GET.get('from_feed')
    feed_source = request.GET.get('feed_source')
    csrf_token = str(csrf(request)['csrf_token'])
    print('*'*40)
    print(user,page,from_feed,feed_source)
    print('*'*40)
    all_feeds = Feed.get_feeds(from_feed)


    paginator = Paginator(all_feeds, FEEDS_NUM_PATES)

    try:
        feeds = paginator.page(page)
    except PageNotAnInteger:
        return HttpResponseBadRequest()
    except EmptyPage:
        feeds = []

    html = ''
    for feed in feeds:
        context = {
            'feed': feed,
            'user': request.user,
            'csrf_token': csrf_token
        }
        template = render_to_string('feeds/partial_feed.html', context)

        html = f'{html}{template}'

    return HttpResponse(html)


def _html_feeds(last_feed, user, csrf_token, feed_source='all'):
    feeds = Feed.get_feeds_after(last_feed)

    if feed_source != 'all':
        if feed_source == 'followed':
            feeds = feeds.filter(user__in=Follow.user_followed(user))
        else:
            feeds = feeds.filter(user__id=feed_source)

    html = ''

    for feed in feeds:
        context = {
            'feed': feed,
            'user': user,
            'csrf_token': csrf_token
        }
        template = render_to_string('feeds/partial_feed.html', context)

        html = f'{html}{template}'
    return html


@login_required
@ajax_required
def remove(request):
    feed_id = request.POST.get('feed')
    feed = Feed.objects.filter(pk=feed_id).first()

    if not feed:
        return HttpResponseBadRequest

    if feed.user == request.user or request.user.is_superuser:
        parent = feed.parent
        likes = feed.get_likes()

        for like in likes:
            like.delete()

        feed.delete()
        if parent:
            parent.calculate_comments()

        return HttpResponse()

    return HttpResponseForbidden()
