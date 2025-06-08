# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate
from django.views.generic import RedirectView


class Top(LoginRequiredMixin, TemplateView):
    """サイトのトップページ"""
    template_name = "top.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["applications"] = [
            {"name": _("外部公開サイト"),
             "url_id": "public:top",
             "description": _("外部向けに研究室から情報発信するページです．")},
            {"name": _("研究室wiki"),
             "url_id": "wiki:root",
             "description": _("研究室で蓄積されたノウハウを書き留めるためのwikiです．")},
            {"name": _("レポート管理"),
             "url_id": "report:top",
             "description": _("報告書や資料，付随するコメント等を管理します．")},
            {"name": _("業績・文献管理"),
             "url_id": "paper:top",
             "description": _("研究室内の業績と参考文献を管理します．")},
            {"name": _("データ出力"),
             "url_id": "output:top",
             "description": _("データを任意のフォーマットで出力できます．")},
            {"name": _("ComNets マーケット"),
             "url_id": "public:market",
             "description": _("研究室で購入できる商品を見ることができます．")},
            {"name": _("データベース"),
             "url_id": "admin:index",
             "description": _("このシステムで管理されているすべてのデータを閲覧することができます．")},
            {"name": _("フォトギャラリー"),
             "url_id": "public:photo_gallery",
             "description": _("研究室イベントの写真を閲覧することができます．")},
        ]
        return context


class LangateRedirectView(RedirectView):
    """言語を指定してリダイレクト"""
    lang = 'ja'
    
    def get(self, *args, **kwargs):
        activate(self.lang)
        response = super(LangateRedirectView, self).get(*args, **kwargs)
        return response
