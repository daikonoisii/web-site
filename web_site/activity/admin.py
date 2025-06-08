from django.contrib import admin
from .models import ProfessionalActivity, Fund, Collaboration
from django.shortcuts import redirect
from django.urls import reverse


class ProfessionalActivityAdmin(admin.ModelAdmin):
    fields = ('title', 'start_date', 'end_date', )
    list_display = ('title', 'start_date', 'end_date', )
    list_filter = ('start_date', 'end_date', )
    search_fields = ('title', )
    ordering = ('-start_date',)
    actions = ['list_download']  # 一括操作のアクションを登録
    
    def list_download(self, request, queryset):
        """リスト生成のaction"""
        pk_list = [q.pk for q in queryset]  # pkのリストに変換
        request.session['pk_list'] = pk_list  # リスト含めたいpkをセッションとして記録することでviewに渡す．
        return redirect(reverse('output:format_list') + '?category=activity')  # ダウンロードページにリダイレクト
    
    list_download.short_description = "選択された %(verbose_name_plural)s のリストをダウンロード"


class FundAdmin(admin.ModelAdmin):
    fields = ('role', 'category', 'fund_name', 'title', 'start_date', 'end_date', )
    list_display = ('role', 'category', 'fund_name', 'title', 'start_date', 'end_date', )
    list_filter = ('role', 'category', 'fund_name', 'start_date', 'end_date', )
    search_fields = ('title', )
    ordering = ('-start_date',)


class CollaborationAdmin(admin.ModelAdmin):
    fields = ('company', 'title', 'start_date', 'end_date', )
    list_display = ('company', 'title', 'start_date', 'end_date', )
    list_filter = ('company', 'start_date', 'end_date', )
    search_fields = ('title', )
    ordering = ('-start_date',)


admin.site.register(ProfessionalActivity, ProfessionalActivityAdmin)
admin.site.register(Fund, FundAdmin)
admin.site.register(Collaboration, CollaborationAdmin)
