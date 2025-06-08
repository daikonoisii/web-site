# -*- coding: utf-8 -*-

from django.urls import path

from . import views

app_name = 'report'

urlpatterns = [
    path('', views.ReportsList.as_view(), name='top'),
    path('<int:report_id>/detail/', views.ReportDetail.as_view(), name='report_detail'),
    path('<int:report_id>/ajax_c_post', views.Ajax_Comment_Post.as_view(), name='ajax_comment_post'),
    path('<int:report_id>/ajax_c_update', views.Ajax_Comment_Update.as_view(), name='ajax_comment_update'),
    path('report/new', views.NewReportCreate.as_view(), name='report_new'),
    path('<int:report_id>/edit/', views.ReportEdit.as_view(), name='report_edit'),
    path('<int:report_id>/edit/preview', views.MarkdownPreview.as_view(), name='markdown_preview'),
    path('<int:pk>/delete/', views.ReportDelete.as_view(), name='report_delete'),
    path('ajax_search', views.Ajax_Report_Search.as_view(), name='ajax_report_search'),
    path('search_list', views.Report_Search_View.as_view(), name='search_list'),
    path('submission_list', views.SubmissionListView.as_view(), name='submission_list'),
    path('my_reports', views.My_Reports_View.as_view(), name='my_reports'),
    path('ajax_my_reports', views.Ajax_My_Reports_View.as_view(), name='ajax_my_reports'),
    path('media/<int:pk>/file', views.ReportPdfView.as_view(), name = 'media_pdf'),
]
