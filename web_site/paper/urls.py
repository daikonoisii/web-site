# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'paper'

urlpatterns = [
    path('', views.PaperTop.as_view(), name='top'),
    path('<pk>/detail/', views.PaperDetail.as_view(), name='paper_detail'),
    path('media/<int:pk>.pdf', views.PaperPdfView.as_view(), name='media_pdf'),
    path('post_print_media/<int:pk>.pdf', views.PostPrintView.as_view(), name='post_print_pdf'),
    path('pre_print_media/<int:pk>.pdf', views.PrePrintView.as_view(), name='pre_print_pdf'),
    path('presentation_pdf_media/<int:pk>.pdf', views.PresentationPdfView.as_view(), name='presentation_pdf'),
    path('search_list', views.PaperSearch.as_view(), name='search_list'),
    path('ajax_search', views.AjaxPaperSearch.as_view(), name='ajax_paper_search'),
    path('create/journal_paper', views.JournalPaperCreate.as_view(), name='create_journal_paper'),
    path('create/our_journal_paper', views.OurJournalPaperCreate.as_view(), name='create_our_journal_paper'),
    path('create/journal_title', views.JournalTitleCreate.as_view(), name='create_journal_title'),
    path('create/conference_title', views.ConferenceTitleCreate.as_view(), name='create_conference_title'),
    path('create/conference_paper', views.ConferencePaperCreate.as_view(), name='create_conference_paper'),
    path('create/our_conference_paper', views.OurConferencePaperCreate.as_view(), name='create_our_conference_paper'),
    path('create/url_reference', views.UrlReferenceCreate.as_view(), name='create_url_reference'),
    path('<int:pk>/update/journal_paper', views.JournalPaperUpdate.as_view(), name='update_journal_paper'),
    path('<int:pk>/update/our_journal_paper', views.OurJournalPaperUpdate.as_view(), name='update_our_journal_paper'),
    path('<int:pk>/update/journal_title', views.JournalTitleUpdate.as_view(), name='update_journal_title'),
    path('<int:pk>/update/conference_title', views.ConferenceTitleUpdate.as_view(), name='update_conference_title'),
    path('<int:pk>/update/conference_paper', views.ConferencePaperUpdate.as_view(), name='update_conference_paper'),
    path('<int:pk>/update/our_conference_paper', views.OurConferencePaperUpdate.as_view(),
         name='update_our_conference_paper'),
    path('<int:pk>/update/url_reference', views.UrlReferenceUpdate.as_view(), name='update_url_reference'),
    path('bibtex_how_to', views.BibtexHowTo.as_view(), name = 'bibtex_how_to'),
]
