# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'output'

urlpatterns = [
    path('', views.OutputTop.as_view(), name='top'),
    path('format_list', views.FormatList.as_view(), name='format_list'),
    path('format_form', views.FormatFormView.as_view(), name='format_form'),
    path('mix_format_form', views.MixFormatFormView.as_view(), name='mix_format_form'),
    path('list_download', views.ListDownload.as_view(), name='list_download'),
]
