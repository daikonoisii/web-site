from django.contrib import admin
from market.models import Item


class ItemAdmin(admin.ModelAdmin):
    fields = ('title', 'category', 'price', 'user', 'active', 'description')
    list_display = ('title', 'price', 'user', )
    list_filter = ('user', )
    search_fields = ('title', )
    
    def get_form(self, request, *args, **kwargs):
        form = super(ItemAdmin, self).get_form(request, *args, **kwargs)
        form.base_fields['user'].initial = request.user  # フォームのデフォルト値をログインユーザに
        return form
    
    def save_related(self, request, form, formsets, change):
        """save時の挙動をオーバーライド"""
        super(ItemAdmin, self).save_related(request, form, formsets, change)


admin.site.register(Item, ItemAdmin)
