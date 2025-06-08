# -*- coding: utf-8 -*-
"""web_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from . import views
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = i18n_patterns(
    path('management', views.Top.as_view(), name='members_top'),  # メンバー向けトップページ
    url(r'^management/$', RedirectView.as_view(url='/management', permanent=True)),
    path('admin/', admin.site.urls),
    url(r'', include('users.urls')),
    url(r'', include('market.urls')),
    path('', include('public.urls')),
    path('management/api/', include('api.urls')),
    path('management/report/', include('report.urls')),
    path('management/paper/', include('paper.urls')),
    path('management/award/', include('award.urls')),
    path('management/output/', include('output.urls')),
    path('management/picture/', include('picture.urls')),
    path('notify/', include('django_nyt.urls')),
    path('labwiki/', include('wiki.urls')),   # wiki
    url('index.html', views.LangateRedirectView.as_view(url=reverse_lazy('public:kwatabe'),
                                                        permanent=True, lang='en')),  # 旧サイトからのリダイレクト
    url('indexjp.html', views.LangateRedirectView.as_view(url=reverse_lazy('public:kwatabe'),
                                                          permanent=True, lang='ja')),  # 旧サイトからのリダイレクト
    url('profile.html', views.LangateRedirectView.as_view(url=reverse_lazy('public:kwatabe_profile'),
                                                          permanent=True, lang='en')),  # 旧サイトからのリダイレクト
    url('purofuiru.html', views.LangateRedirectView.as_view(url=reverse_lazy('public:kwatabe_profile'),
                                                            permanent=True, lang='ja')),  # 旧サイトからのリダイレクト
    url('researchfieldsofinterest.html', views.LangateRedirectView.as_view(url=reverse_lazy('public:kwatabe'),
                                                                           permanent=True, lang='en')),  # 旧サイトからのリダイレクト
    url('kenkyuuryouiki.html', views.LangateRedirectView.as_view(url=reverse_lazy('public:kwatabe'),
                                                                 permanent=True, lang='ja')),  # 旧サイトからのリダイレクト
    url('publications.html', views.LangateRedirectView.as_view(url=reverse_lazy('public:kwatabe_publications'),
                                                               permanent=True, lang='en')),  # 旧サイトからのリダイレクト
    url('kenkyuugyouseki.html', views.LangateRedirectView.as_view(url=reverse_lazy('public:kwatabe_publications'),
                                                                  permanent=True, lang='ja')),  # 旧サイトからのリダイレクト
    url('link.html', views.LangateRedirectView.as_view(url=reverse_lazy('public:kwatabe'),
                                                       permanent=True, lang='en')),  # 旧サイトからのリダイレクト
    url('rinku.html', views.LangateRedirectView.as_view(url=reverse_lazy('public:kwatabe'),
                                                        permanent=True, lang='ja')),  # 旧サイトからのリダイレクト
    url(r'^i18n/', include('django.conf.urls.i18n')),
    prefix_default_language=False  # 日本語のprefix(ja)はurlに入れない．
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)