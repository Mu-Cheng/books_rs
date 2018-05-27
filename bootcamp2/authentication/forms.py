from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def signup_domain_validator(value):
    if '*' in settings.ALLOWED_SIGNUP_DOMAINS:
        return

    domain = value[value.index('@'):]

    if domain not in settings.ALLOWED_SIGNUP_DOMAINS:
        allowed_domain = ','.join(settings.ALLOWED_SIGNUP_DOMAINS)
        msg = _('Invalid domain'
                'Allowed domains on this network: {0}').format(allowed_domain)
        raise ValidationError(msg)


def forbidden_username_validator(value):
    forbidden_usernames = {
        'admin', 'settings', 'news', 'about', 'help', 'signin', 'signup',
        'signout', 'terms', 'privacy', 'cookie', 'new', 'login', 'logout',
        'administrator', 'join', 'account', 'username', 'root', 'blog',
        'user', 'users', 'billing', 'subscribe', 'reviews', 'review', 'blog',
        'blogs', 'edit', 'mail', 'email', 'home', 'job', 'jobs', 'contribute',
        'newsletter', 'shop', 'profile', 'register', 'auth', 'authentication',
        'campaign', 'config', 'delete', 'remove', 'forum', 'forums',
        'download', 'downloads', 'contact', 'blogs', 'feed', 'feeds', 'faq',
        'intranet', 'log', 'registration', 'search', 'explore', 'rss',
        'support', 'status', 'static', 'media', 'setting', 'css', 'js',
        'follow', 'activity', 'questions', 'articles', 'network', }
    if value.lower() in forbidden_usernames:
        raise ValidationError(_('This is a reserved word.'))


def invalid_username_validator(value):
    if '@' in value or '+' in value or '-' in value:
        raise ValidationError(_('Enter a valid username.'))


# 准确匹配
def unique_email_validator(value):
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError(_('User with this Email already exists.'))


def unique_username_ignore_case_validator(value):
    if User.objects.filter(username__iexact=value).exists():
        raise ValidationError(_('User with this Username already exists.'))


class SignUpForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,
        required=True,
        label=_('Username'),
        help_text=_('Usernames may contain alphanumeric, _ and . characters')
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_('Password'),
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_('Confirm your password'),
        required=True
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True,
        max_length=75,
        label=_('Email')
    )
    college = forms.ChoiceField(
        choices=[('华信软件学院','华信软件学院'),('院办印刷厂','院办印刷厂'),('机械工程学院','机械工程学院'),
        ('管理学院','管理学院'),('环境科学与安全工程学院','环境科学与安全工程学院'),('化学化工学院','化学化工学院'),
        ('海运学院','海运学院'),('新能源与低碳技术研究院','新能源与低碳技术研究院'),('基建处','基建处'),
        ('材料科学与工程学院','材料科学与工程学院'),('人事处','人事处'),('国际工商学院','国际工商学院'),
        ('聋人工学院','聋人工学院'),('纪监审计处','纪监审计处'),('继续教育学院','继续教育学院'),
        ('工程训练中心','工程训练中心'),('汉语言文化学院','汉语言文化学院'),('体育教学部','体育教学部'),
        ('电子信息工程学院','电子信息工程学院'),('学刊编辑部','学刊编辑部'),('学生处','学生处'),
        ('马克思主义学院','马克思主义学院'),('艺术学院','艺术学院'),('图书馆','图书馆'),('国际交流处','国际交流处'),
        ('学术刊物编辑部','学术刊物编辑部'),('档案馆','档案馆'),('保卫处','保卫处'),('校办公室','校办公室'),
        ('理学院','理学院'),('后勤管理处','后勤管理处'),('法政学院','法政学院'),('离退休办公室','离退休办公室'),
        ('研究生院','研究生院'),('教务处','教务处'),('外国语学院','外国语学院'),('自动化学院','自动化学院'),
        ('校工会','校工会'),('国有资产管理处','国有资产管理处'),('财务处','财务处'),('后勤集团','后勤集团'),
        ('宣传部','宣传部'),('计算机与通信工程学院','计算机与通信工程学院'),('科技处','科技处')],
        label=_('College'),
    )
    identity = forms.ChoiceField(
        # attrs={"class":"dropdown"},
        choices=[('正式职工','正式职工'),('本科生','本科生'),('硕士生','硕士生')],
        label=_('Identity'),

    )
    identity.widget.attrs={"class":"form-control"}
        # widget=forms.EmailInput(attrs={'class': 'form-control'}),
        # required=True,
        # max_length=75,
    # )
# 模型表单 除了
    class Meta:
        model = User
        exclude = ['last_login', 'date_joined']
        fields = ['username',  'password', 'confirm_password','email', 'college','identity' ]

    def __init__(self, *args, **kw):
        super(SignUpForm, self).__init__(*args, **kw)
        self.fields['username'].validators += [
            forbidden_username_validator, invalid_username_validator,
            unique_username_ignore_case_validator
        ]
        self.fields['email'].validators += [
            unique_email_validator, signup_domain_validator]

    def clean(self):
        super(SignUpForm, self).clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('password')
        if password and password != confirm_password:
            self._errors['password'] = self.error_class(
                [_('Passwords don\'t match')]
            )
        return self.cleaned_data
