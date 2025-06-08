from django.contrib import admin
from .models import Format


class FormatAdmin(admin.ModelAdmin):
    fields = ('name', 'category', 'header', 'format', 'footer', 'user', 'created_date')
    readonly_fields = ('user', 'created_date')
    list_display = ('name', 'category')
    list_filter = ('name', 'category')
    search_fields = ('name', 'category')


admin.site.register(Format, FormatAdmin)
