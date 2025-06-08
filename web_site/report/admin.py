# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Report, Comment


class ReportAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'created_date',)
    list_display = ('title', 'user', 'abstract', 'research', 'created_date')
    list_filter = ('user', 'created_date', 'research')
    search_fields = ('title', 'abstract', 'created_date')
    ordering = ('created_date',)


class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'published_date',)
    list_display = ('report', 'user', 'comment', 'published_date')
    list_filter = ('user', 'published_date')
    search_fields = ('comment', 'published_date')
    ordering = ('published_date',)


admin.site.register(Report, ReportAdmin)
admin.site.register(Comment, CommentAdmin)
