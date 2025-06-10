# -*- coding: utf-8 -*-
from django.urls import path, re_path
from . import views

app_name = 'picture'

urlpatterns = [
    path(r'media/picture/<int:pk>', views.PictureView.as_view(), name='image'),
    path(r'media/wiki/images/<aid>/<pk>/<pic_name>', views.WikiPictureView.as_view(), name='wiki_image'),
    path('my-images/<str:image_name>/', views.serve_image_with_cache, name='serve_image_with_cache'), #この部分を追記
]
