# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'api'


urlpatterns = [
    path('light-on', views.LightOn.as_view(), name='light-on'),
    path('light-off', views.LightOff.as_view(), name='light-off'),
]
