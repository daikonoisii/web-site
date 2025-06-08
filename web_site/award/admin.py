from django.contrib import admin
from .models import Award
from django.shortcuts import redirect
from django.urls import reverse


class AwardAdmin(admin.ModelAdmin):
    fields = ('title', 'winner', 'user', 'org', 'date')
    list_display = ('title', 'winner', 'org', 'date',)
    list_filter = ('user', 'date',)
    search_fields = ('title', 'winner', 'user', 'org')
    ordering = ('-date',)
    actions = ['list_download']  # 一括操作のアクションを登録
    filter_horizontal = ('user',)  # m2mの横並びフィルタ
    
    def list_download(self, request, queryset):
        """リスト生成のaction"""
        pk_list = [q.pk for q in queryset]  # pkのリストに変換
        request.session['pk_list'] = pk_list  # リスト含めたいpkをセッションとして記録することでviewに渡す．
        return redirect(reverse('output:format_list') + '?category=award')  # ダウンロードページにリダイレクト
    list_download.short_description = "選択された %(verbose_name_plural)s のリストをダウンロード"


admin.site.register(Award, AwardAdmin)
