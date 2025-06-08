from django.contrib import admin
from .models import Reference, JournalPaper, OurJournalPaper, JournalTitle, \
    ConferencePaper, OurConferencePaper, ConferenceTitle, Tag
from django.shortcuts import redirect
from django.urls import reverse


class ReferenceAdmin(admin.ModelAdmin):
    fields = ('citation_key', 'title', 'abstract', 'pdf', 'tag', 'user', 'created_date')
    readonly_fields = ('citation_key', 'user', 'created_date',)
    list_display = ('citation_key', 'title', 'user', 'created_date')
    list_filter = ('user', 'tag', 'created_date')
    search_fields = ('citation_key', 'title', 'abstract')
    ordering = ('-created_date',)
    filter_horizontal = ('tag',)  # m2mの横並びフィルタ
    
    def save_related(self, request, form, formsets, change):
        """save時の挙動をオーバーライド"""
        form.instance.user = request.user  # 登録ユーザを自動入力
        form.instance.save()  # データを更新
        form.instance.assign_citation_key()  # citation_keyの自動設定
        super(ReferenceAdmin, self).save_related(request, form, formsets, change)


class JournalPaperAdmin(admin.ModelAdmin):
    fields = ('citation_key',
              'title',
              'author',
              ('journal_title', 'volume', 'number', 'page'),
              ('year', 'month',),
              'abstract',
              'pdf',
              'tag',
              'user',
              'created_date')
    readonly_fields = ('citation_key', 'user', 'created_date',)
    list_display = ('citation_key', 'author', 'title', 'journal_title', 'year', 'user', 'created_date')
    list_filter = ('tag', 'created_date', 'user')
    search_fields = ('author', 'citation_key', 'title', 'abstract')
    ordering = ('-created_date',)
    actions = ['list_download']  # 一括操作のアクションを登録
    filter_horizontal = ('tag',)  # m2mの横並びフィルタ
    
    def list_download(self, request, queryset):
        """リスト生成のaction"""
        pk_list = [q.pk for q in queryset]  # pkのリストに変換
        request.session['pk_list'] = pk_list  # リスト含めたいpkをセッションとして記録することでviewに渡す．
        return redirect(reverse('output:format_list') + '?category=journal_paper')  # ダウンロードページにリダイレクト
    list_download.short_description = "選択された %(verbose_name_plural)s のリストをダウンロード"
    
    def save_related(self, request, form, formsets, change):
        """save時の挙動をオーバーライド"""
        form.instance.user = request.user  # 登録ユーザを自動入力
        form.instance.save()
        form.instance.assign_citation_key()  # citation_keyの自動設定
        super(JournalPaperAdmin, self).save_related(request, form, formsets, change)


class ConferencePaperAdmin(admin.ModelAdmin):
    fields = ('citation_key',
              'title',
              'author',
              ('conference_title', 'page', 'presentation_id'),
              'abstract',
              'pdf',
              'tag',
              'user',
              'created_date')
    readonly_fields = ('citation_key', 'user', 'created_date',)
    list_display = ('citation_key', 'author', 'title', 'conference_title', 'user', 'created_date')
    list_filter = ('tag', 'created_date', 'user')
    search_fields = ('author', 'citation_key', 'title', 'abstract')
    ordering = ('-created_date',)
    actions = ['list_download']  # 一括操作のアクションを登録
    filter_horizontal = ('tag',)  # m2mの横並びフィルタ
    
    def list_download(self, request, queryset):
        """リスト生成のaction"""
        pk_list = [q.pk for q in queryset]  # pkのリストに変換
        request.session['pk_list'] = pk_list  # リスト含めたいpkをセッションとして記録することでviewに渡す．
        return redirect(reverse('output:format_list') + '?category=conference_paper')  # ダウンロードページにリダイレクト
    list_download.short_description = "選択された %(verbose_name_plural)s のリストをダウンロード"
    
    def save_related(self, request, form, formsets, change):
        """save時の挙動をオーバーライド"""
        form.instance.user = request.user  # 登録ユーザを自動入力
        form.instance.save()
        form.instance.assign_citation_key()  # citation_keyを自動設定
        super(ConferencePaperAdmin, self).save_related(request, form, formsets, change)


class OurJournalPaperAdmin(JournalPaperAdmin):
    fields = ('citation_key',
              'title',
              'author',
              'author_user',
              ('journal_title', 'volume', 'number', 'page'),
              'published_date',
              ('letter', 'invited'),
              'abstract',
              'pdf',
              'post_print',
              'pre_print',
              'doi',
              'url',
              'fwci',
              'scopus_cite',
              'tag',
              'user',
              'created_date')
    readonly_fields = ('citation_key', 'user', 'created_date',)
    list_display = ('citation_key', 'author', 'title', 'journal_title', 'year', 'user', 'created_date')
    list_filter = ('letter', 'invited', 'tag', 'created_date', 'user')
    search_fields = ('author', 'citation_key', 'title', 'abstract')
    ordering = ('-created_date',)
    actions = ['list_download']  # 一括操作のアクションを登録
    filter_horizontal = ('author_user', 'tag',)  # m2mの横並びフィルタ
    
    def list_download(self, request, queryset):
        """リスト生成のaction"""
        pk_list = [q.pk for q in queryset]  # pkのリストに変換
        request.session['pk_list'] = pk_list  # リスト含めたいpkをセッションとして記録することでviewに渡す．
        return redirect(reverse('output:format_list') + '?category=our_journal_paper')  # ダウンロードページにリダイレクト
    
    list_download.short_description = "選択された %(verbose_name_plural)s のリストをダウンロード"
    
    def save_related(self, request, form, formsets, change):
        """save時の挙動をオーバーライド"""
        form.instance.year = form.instance.published_date.year
        form.instance.month = form.instance.published_date.month
        form.instance.save()  # データを更新
        super(OurJournalPaperAdmin, self).save_related(request, form, formsets, change)


class OurConferencePaperAdmin(ConferencePaperAdmin):
    fields = ('citation_key',
              'title',
              'author',
              'presenter',
              'author_user',
              ('conference_title', 'page', 'presentation_id'),
              'published_date',
              ('short_paper', 'poster', 'invited'),
              'abstract',
              'subject',
              'pdf',
              'post_print',
              'pre_print',
              'presentation_pdf',
              'doi',
              'url',
              'fwci',
              'scopus_cite',
              'core_rank',
              'tag',
              'user',
              'created_date')
    readonly_fields = ('citation_key', 'user', 'created_date',)
    list_display = ('citation_key',
                    'author',
                    'presenter',
                    'title',
                    'conference_title',
                    'user',
                    'published_date',
                    'created_date')
    list_filter = ('short_paper', 'poster', 'invited', 'tag', 'subject', 'published_date', 'created_date', 'user')
    search_fields = ('author', 'citation_key', 'title', 'abstract', 'presenter')
    ordering = ('-published_date',)
    actions = ['list_download']  # 一括操作のアクションを登録
    filter_horizontal = ('author_user', 'tag',)  # m2mの横並びフィルタ
    
    def list_download(self, request, queryset):
        """リスト生成のaction"""
        pk_list = [q.pk for q in queryset]  # pkのリストに変換
        request.session['pk_list'] = pk_list  # リスト含めたいpkをセッションとして記録することでviewに渡す．
        return redirect(reverse('output:format_list') + '?category=our_conference_paper')  # ダウンロードページにリダイレクト
    list_download.short_description = "選択された %(verbose_name_plural)s のリストをダウンロード"


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', )
    ordering = ('name',)


admin.site.register(Reference, ReferenceAdmin)
admin.site.register(JournalPaper, JournalPaperAdmin)
admin.site.register(OurJournalPaper, OurJournalPaperAdmin)
admin.site.register(JournalTitle)
admin.site.register(ConferencePaper, ConferencePaperAdmin)
admin.site.register(OurConferencePaper, OurConferencePaperAdmin)
admin.site.register(ConferenceTitle)
admin.site.register(Tag, TagAdmin)
