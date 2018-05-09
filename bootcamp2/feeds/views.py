from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_page

from bootcamp2.decorators import ajax_required
from bootcamp2.activities.models import Activity
from bootcamp2.articles.models import Article
from bootcamp2.articles.views import tag
from bootcamp2.follow.models import Follow
from bootcamp2.borrow.models import Borrow



from .models import Feed
import redis, time, pickle,MySQLdb,json,random

FEEDS_NUM_PATES = 24
NO_USER = 'AnonymousUser'
# @cache_page(None)
def feeds(request):
    # redis cache db 8
    user = request.user
    # print(request)
    user = '{}'.format(user)
    if user == NO_USER:
        return render(request, 'feeds/nouser_home.html', {
            # 'feeds': feeds,
            # 'from_feed': from_feed,
            # 'page': 1,
        })

    # print(user)
    # print(type(user))

    r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=8)
    r_ans = r_db.get(user)
    bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
    bootcamp2_c = bootcamp2_db.cursor()
    bootcamp2_c.execute('select id from auth_user where username = \'{}\''.format(user))
    user_id = bootcamp2_c.fetchone()
    user_id = user_id[0]
    # print(user_id)
    bootcamp2_c.close()
    bootcamp2_db.close()
    # r_ans = False
    if r_ans:
        paginator = pickle.loads(r_ans)
    else:
        try:
            # user = User.objects.get(username=user)
            # user = user.get_profile().id
            # print('user_id = ', user_id)
            all_feeds = Feed.get_feeds(user_id)
            # print(type(all_feeds))
        except:
            all_feeds = Feed.get_feeds(3)

        paginator = Paginator(all_feeds, FEEDS_NUM_PATES)
        if paginator.num_pages < 2:
            return tag(request,'小说')
        r_db.setnx(user, pickle.dumps(paginator))
    # content = r_db.get(article.title)
    # content = str(content, encoding='utf-8')
    # content = json.loads(content)
    # print('request : {}'.format(request))
    # print('id : {}'.format(user))
    # print('idtype : {}'.format(type(user)))
    # try:
    #     all_feeds = Feed.get_feeds(user)
    # except:
    #     all_feeds = Feed.get_feeds(3)
    #
    # # print(type(all_feeds))
    # paginator = Paginator(all_feeds, FEEDS_NUM_PATES)
    # print('paginator :{}'.format(type(paginator)))
    # print('paginator :{}'.format(paginator))


    page = request.GET.get('page')

    try:
        page = random.randint(1,paginator.num_pages-1)
        feeds = paginator.page(page)
    except PageNotAnInteger:
        feeds = paginator.page(1)
    except EmptyPage:
        feeds = paginator.page(paginator.num_pages)

    # print(feeds.object_list)
    item_list = feeds.object_list
    len_item = len(item_list)
    books = []
    # feeds = []
    for i in range(len_item):
        try:
            book_id = feeds[i].post.split('/')[-2]
            feeds[i].comments = len(Article.objects.filter(id=book_id)[0].get_comments())

        # books.append(book_id)
        # item.comments = len(Article.objects.filter(id=book_id)[0].get_comments())
        except:
            feeds[i].comments = 0
        # feeds.append(item)
    # feeds = paginator.page(1)
    from_feed = -1
    # print(feeds.next_page_number)
    if feeds:
        from_feed = feeds[0].id
    return render(request, 'feeds/feeds.html', {
        'feeds': feeds,
        'from_feed': from_feed,
        'borrow_sum': Borrow.get_borrowed_sum(user_id),
        'page': 1,
    })

# @cache_page(None)
def followed(request):
    # cache redis db 10
    user = request.user
    # print('followed ',user)
    user_id = None
    if user == NO_USER:
        return render(request, 'feeds/followed_feeds.html', {
            'borrows': None,
            # 'from_feed': from_feed,
            'page': 1,
        })

    if request.POST:
        mode = request.POST['mode']
        # print('mode : {}'.format(mode))
        book_name = request.POST['book_name']
        book_id = request.POST['book_id']
        book_link = 'http://118.89.162.148/articles/{}'.format(request.POST['book_id'])
        r_db = redis.Redis(host='10.154.141.214', password='7TCcwQUKZ3NH', port=6379, db=6)
        content = r_db.get(book_name)
        content = str(content, encoding='utf-8')
        content = json.loads(content)
        # print(content)
        book = content['books'][0]
        img_link = book['image'].split('/')[-1]

        bootcamp2_db = MySQLdb.connect(host="127.0.0.1", port=43306, user="root", passwd="xu695847", db="bootcamp2", charset='utf8')
        bootcamp2_c = bootcamp2_db.cursor()
        bootcamp2_c.execute('select id from auth_user where username = \'{}\''.format(user))
        user_id = bootcamp2_c.fetchone()
        userid = user_id[0]
        user_id = userid
        # print('userid',user_id)
        bootcamp2_c.close()
        bootcamp2_db.close()
        # print(userid,book_link,img_link,book_name)
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
            post = '[{}]({}/)'.format(book_name,book_link)
            # print(userid,post)
            try:
                Feed.objects.filter(user_id=userid,post=post).delete()
            except:
                print(post+'del fail')
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
            except:
                print('return book {} fail'.format(book_name))
        # if mode == 'return_book':
            # print('return_book')
    else:
        userid = None
    # print(book_name)
    # Borrow.objects.create()

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
            # print(user_id)
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
        # print(user_id)
        bootcamp2_c.close()
        bootcamp2_db.close()
    return render(request, 'feeds/followed_feeds.html', {
        'borrows': borrows,
        # 'from_feed': from_feed,
        'borrow_sum' : Borrow.get_borrowed_sum(user_id),
        'page': 1,
        'pages_sum': paginator.num_pages,
    })

    #
    # all_feeds = Feed.get_feeds().filter(user__in=Follow.user_followed(user))
    # paginator = Paginator(all_feeds, FEEDS_NUM_PATES)
    # feeds = paginator.page(1)
    # from_feed = -1
    # if feeds:
    #     from_feed = feeds[0].id
    # return render(request, 'feeds/followed_feeds.html', {
    #     'feeds': feeds,
    #     'from_feed': from_feed,
    #     'page': 1,
    # })


def feed(request, pk):
    localtime = time.asctime(time.localtime(time.time()))
    # print("the 1 tiem", localtime)
    feed = get_object_or_404(Feed, pk=pk)
    localtime = time.asctime(time.localtime(time.time()))
    # print("the 2 tiem", localtime)
    return render(request, 'feeds/feed.html', {'feed': feed})


@ajax_required
def load(request):
    user = request.user
    page = request.GET.get('page')
    from_feed = request.GET.get('from_feed')
    feed_source = request.GET.get('feed_source')
    csrf_token = str(csrf(request)['csrf_token'])

    all_feeds = Feed.get_feeds(from_feed)

    if feed_source != 'all':
        if feed_source == 'followed':
            all_feeds = all_feeds.filter(user__in=Follow.user_followed(user))
        else:
            all_feeds = all_feeds.filter(user__id=feed_source)

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


@ajax_required
def load_new(request):
    last_feed = request.GET.get('last_feed')
    user = request.user
    csrf_token = str(csrf(request)['csrf_token'])
    html = _html_feeds(last_feed, user, csrf_token)
    return HttpResponse(html)


@ajax_required
def check(request):
    user = request.user
    last_feed = request.GET.get('last_feed')
    feed_source = request.GET.get('feed_source')
    feeds = Feed.get_feeds_after(last_feed)

    if feed_source != 'all':
        if feed_source == 'followed':
            feeds = feeds.filter(user__in=Follow.user_followed(user))
        else:
            feeds = feeds.filter(user__id=feed_source)

    count = feeds.count()
    return HttpResponse(count)


@login_required
@ajax_required
def post(request):
    last_feed = request.POST.get('last_feed')
    post = request.POST['post'].strip()[:255]
    user = request.user

    csrf_token = str(csrf(request)['csrf_token'])

    if len(post) > 0:
        Feed.objects.create(
            post=post,
            user=user
        )
    html = _html_feeds(last_feed, user, csrf_token)
    return HttpResponse(html)


@login_required
@ajax_required
def comment(request):
    if request.method == 'POST':
        feed_id = request.POST['feed']
        feed = Feed.objects.get(pk=feed_id)
        post = request.POST['post'].strip()  # 去格式

        if len(post) > 0:
            post = post[:255]
            user = request.user
            feed.comment(user=user, post=post)
            user.profile.notify_commented(feed)
            user.profile.notify_also_commented(feed)

        context = {'feed': feed}
        return render(request, 'feeds/partial_feed_comments.html', context)

    feed_id = request.GET.get('feed')
    feed = Feed.objects.get(pk=feed_id)
    return render(request, 'feeds/partial_feed_comments.html', {'feed': feed})


@login_required
@ajax_required
def update(request):
    user = request.user
    first_feed = request.GET.get('first_feed')
    last_feed = request.GET.get('last_feed')
    feed_source = request.GET.get('feed_source')

    feeds = Feed.get_feeds().filter(id__range=(last_feed, first_feed))

    if feed_source != 'all':
        if feed_source == 'followed':
            feeds = feeds.filter(user__in=Follow.user_followed(user))
        else:
            feeds = feeds.filter(user__id=feed_source)

    dump = {}

    for feed in feeds:
        dump[feed.pk] = {'comments': feed.comments}

    return JsonResponse(dump, safe=False)


@login_required
@ajax_required
def track_comments(request):
    feed_id = request.GET.get('feed')
    feed = Feed.objects.get(pk=feed_id)
    return render(request, 'feeds/partial_feed_comments.html', {'feed': feed})


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


##
@login_required
@ajax_required
def like(request):
    user = request.user
    feed_id = request.POST['feed']

    feed = Feed.objects.get(pk=feed_id)
    like = Activity.objects.filter(
        activity_type=Activity.LIKE, feed=feed_id, user=user)

    if like:
        user.profile.unotify_liked(feed)
        like.delete()
    else:
        Activity.objects.create(
            feed=feed_id,
            user=user,
            activity_type=Activity.LIKE
        )
        user.profile.notify_liked(feed)
    return HttpResponse(feed.calculate_likes())
