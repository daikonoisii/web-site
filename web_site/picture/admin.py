from django.contrib import admin
from .models import Picture


class PictureAdmin(admin.ModelAdmin):
    fields = ('category', 'caption', 'user', 'file', 'private', 'web', 'top_page', 'created_date')
    readonly_fields = ('user', 'created_date')
    list_display = ('caption', 'category', 'private', 'web', 'top_page', 'file')
    list_filter = ('user', 'web', 'top_page', 'created_date')
    search_fields = ('caption', 'user', 'created_date')
    ordering = ('-created_date',)


admin.site.register(Picture, PictureAdmin)
