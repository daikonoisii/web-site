# -*- coding: utf-8 -*-
from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.PublicTop.as_view(), name='top'),
    path('information', views.PublicInformation.as_view(), name='information'),
    path('about_us', views.PublicAboutUs.as_view(), name='about_us'),
    path('researches/<pk>/', views.PresentationList.as_view(), name='presentation_list'),
    path('achievements', views.PublicAchievements.as_view(), name='achievements'),
    path('members', views.PublicMembers.as_view(), name='members'),
    url('nakagawa_lab_members', views.PublicNakagawaLabMembers.as_view(), name='nakagawa_lab_members'),
    path('former_members', views.PublicFormerMembers.as_view(), name='former_members'),
    path('contacts', views.PublicContacts.as_view(), name='contacts'),
    path('kwatabe', views.PublicKWatabe.as_view(), name='kwatabe'),
    path('kwatabe/profile', views.PublicKWatabeProfile.as_view(), name='kwatabe_profile'),
    path('kwatabe/publications', views.PublicKWatabePublications.as_view(), name='kwatabe_publications'),
    path('knakagawa', views.PublicKNakagawaPublications.as_view(), name='knakagawa'),
    path('kwatabe/schedule', views.PublicKWatabeSchedule.as_view(), name='kwatabe_schedule'),
    path('kwatabe/exam', views.PublicKWatabeExam.as_view(), name='kwatabe_exam'),
    path('kwatabe/exam2', views.PublicKWatabeExam2.as_view(), name='kwatabe_exam2'),
    path('schedule', views.PublicSchedule.as_view(), name='schedule'),
    path('market', views.PublicMarket.as_view(), name='market'),
    path('photo_gallery', views.PhotoGalleryView.as_view(), name='photo_gallery')
]
