from django.views.generic import View, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from .forms import FormatForm
from paper.models import OurConferencePaper, OurJournalPaper, ConferencePaper, JournalPaper, UrlReference
from award.models import Award
from activity.models import ProfessionalActivity
from .models import Format
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from lib.latex import escape_char2latex
from lib.japanese import is_japanese
import json


class OutputTop(LoginRequiredMixin, ListView):
    """データ出力トップページ表示"""
    model = Format
    template_name = 'output/output_top.html'
    
    def get_queryset(self):
        release_period = timezone.now().date() - timezone.timedelta(days=14)
        return Format.objects.filter(
            created_date__range=(release_period, timezone.datetime.now())
        ).order_by('-created_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new'] = timezone.now().date()
        context['past'] = timezone.now().date() - timezone.timedelta(days=14)
        return context


class FormatList(LoginRequiredMixin, ListView):
    """フォーマットリストページ表示"""
    model = Format
    template_name = 'output/format_list.html'
    
    def get_queryset(self):
        category = self.request.GET['category']
        return Format.objects.filter(category=category).order_by('-created_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.request.GET['category']
        return context
    
    def get(self, request, *args, **kwargs):
        if 'category' not in self.request.GET:
            raise Http404  # カテゴリのパラメータがなければ404
        else:
            category = self.request.GET['category']
        if 'session_clear' in self.request.GET:
            if self.request.GET['session_clear'] == 'on':
                if 'pk_list' in self.request.session:
                    del self.request.session['pk_list']  # セッションのpk_listをクリア
        response = super().get(self, request, *args, **kwargs)
        pk_list = self.request.session.get('pk_list', False)  # セッションに保存したpkのリストを取得
        url = reverse('output:format_list')
        if pk_list is not False:  # pk_listの指定があればメッセージを表示
            messages.info(self.request,
                          '下記のPrimary Keyのデータが出力対象として指定されています．'
                          '出力するフォーマットを選択するか，新規作成してください．\n'
                          '%s\n'
                          '<a href="%s?category=%s&session_clear=on">キャンセル</a>' % (pk_list, url, category)
                          )
        return response


def our_conference_paper_output_list(list_format, sort_key, pk_list, latex=False):
    """OurConferencePaperをフォーマットに従ったリストにする"""
    formatted_list = []
    for pk in pk_list:
        try:
            paper = OurConferencePaper.objects.get(pk=pk)  # データを取得
            text = list_format
            sort_key_text = sort_key
            for k, v in OurConferencePaper.VARIABLES.items():  # VARIABLES に登録のあるものをすべて置き換え
                if latex:
                    text = text.replace(k, escape_char2latex(v(paper)))  # latexがTrueならエスケープ
                else:
                    text = text.replace(k, v(paper))
                sort_key_text = sort_key_text.replace(k, v(paper))  # VARIABLES に登録のあるものをすべて置き換え
            formatted_list.append((sort_key_text, text))  # リストに追加
        except OurConferencePaper.DoesNotExist:  # 存在しなければスルー．
            pass
    return formatted_list


def our_journal_paper_output_list(list_format, sort_key, pk_list, latex=False):
    """OurJournalPaperをフォーマットに従ったリストにする"""
    formatted_list = []
    for pk in pk_list:
        try:
            paper = OurJournalPaper.objects.get(pk=pk)  # データを取得
            text = list_format
            sort_key_text = sort_key
            for k, v in OurJournalPaper.VARIABLES.items():  # VARIABLES に登録のあるものをすべて置き換え
                if latex:
                    text = text.replace(k, escape_char2latex(v(paper)))  # latexがTrueならエスケープ
                else:
                    text = text.replace(k, v(paper))  # VARIABLES に登録のあるものをすべて置き換え
                sort_key_text = sort_key_text.replace(k, v(paper))  # VARIABLES に登録のあるものをすべて置き換え
            formatted_list.append((sort_key_text, text))  # リストに追加
        except OurJournalPaper.DoesNotExist:  # 存在しなければスルー．
            pass
    return formatted_list


def conference_paper_output_list(list_format, sort_key, pk_list, latex=False):
    """ConferencePaperをフォーマットに従ったリストにする"""
    formatted_list = []
    for pk in pk_list:
        try:
            paper = ConferencePaper.objects.get(pk=pk)  # データを取得
            text = list_format
            sort_key_text = sort_key
            for k, v in ConferencePaper.VARIABLES.items():  # VARIABLES に登録のあるものをすべて置き換え
                if latex:
                    text = text.replace(k, escape_char2latex(v(paper)))  # latexがTrueならエスケープ
                else:
                    text = text.replace(k, v(paper))  # VARIABLES に登録のあるものをすべて置き換え
                sort_key_text = sort_key_text.replace(k, v(paper))  # VARIABLES に登録のあるものをすべて置き換え
            formatted_list.append((sort_key_text, text))  # リストに追加
        except ConferencePaper.DoesNotExist:  # 存在しなければスルー．
            pass
    return formatted_list


def journal_paper_output_list(list_format, sort_key, pk_list, latex=False):
    """JournalPaperをフォーマットに従ったリストにする"""
    formatted_list = []
    for pk in pk_list:
        try:
            paper = JournalPaper.objects.get(pk=pk)  # データを取得
            text = list_format
            sort_key_text = sort_key
            for k, v in JournalPaper.VARIABLES.items():  # VARIABLES に登録のあるものをすべて置き換え
                if latex:
                    text = text.replace(k, escape_char2latex(v(paper)))  # latexがTrueならエスケープ
                else:
                    text = text.replace(k, v(paper))  # VARIABLES に登録のあるものをすべて置き換え
                sort_key_text = sort_key_text.replace(k, v(paper))  # VARIABLES に登録のあるものをすべて置き換え
            formatted_list.append((sort_key_text, text))  # リストに追加
        except JournalPaper.DoesNotExist:  # 存在しなければスルー．
            pass
    return formatted_list


def url_reference_output_list(list_format, sort_key, pk_list, latex=False):
    """UrlReferenceをフォーマットに従ったリストにする"""
    formatted_list = []
    for pk in pk_list:
        try:
            paper = UrlReference.objects.get(pk=pk)  # データを取得
            text = list_format
            sort_key_text = sort_key
            for k, v in UrlReference.VARIABLES.items():  # VARIABLES に登録のあるものをすべて置き換え
                if latex:
                    text = text.replace(k, escape_char2latex(v(paper)))  # latexがTrueならエスケープ
                else:
                    text = text.replace(k, v(paper))  # VARIABLES に登録のあるものをすべて置き換え
                sort_key_text = sort_key_text.replace(k, v(paper))  # VARIABLES に登録のあるものをすべて置き換え
            formatted_list.append((sort_key_text, text))  # リストに追加
        except UrlReference.DoesNotExist:  # 存在しなければスルー．
            pass
    return formatted_list


def award_output_list(list_format, sort_key, pk_list):
    """"Awardをフォーマットに従ったリストにする"""
    formatted_list = []
    for pk in pk_list:
        try:
            award = Award.objects.get(pk=pk)  # データを取得
            for u in award.user.all():
                text = list_format
                sort_key_text = sort_key
                for k, v in Award.VARIABLES.items():
                    if k == '{{ each_user }}':  # userのときだけuを引数に
                        text = text.replace(k, v(award, u))  # VARIABLES に登録のあるものをすべて置き換え
                        sort_key_text = sort_key_text.replace(k, v(award, u))  # VARIABLES に登録のあるものをすべて置き換え
                    else:
                        text = text.replace(k, v(award))  # VARIABLES に登録のあるものをすべて置き換え
                        sort_key_text = sort_key_text.replace(k, v(award))  # VARIABLES に登録のあるものをすべて置き換え
                formatted_list.append((sort_key_text, text))  # リストに追加
                if '{{ each_user }}' not in list_format:  # {{ user }}を含まなければ，複数回出力しない．
                    break
        except Award.DoesNotExist:  # 存在しなければスルー．
            pass
    return formatted_list


def activity_output_list(list_format, sort_key, pk_list):
    """"Activityをフォーマットに従ったリストにする"""
    formatted_list = []
    for pk in pk_list:
        try:
            activity = ProfessionalActivity.objects.get(pk=pk)  # データを取得
            text = list_format
            sort_key_text = sort_key
            for k, v in ProfessionalActivity.VARIABLES.items():
                text = text.replace(k, v(activity))  # VARIABLES に登録のあるものをすべて置き換え
                sort_key_text = sort_key_text.replace(k, v(activity))  # VARIABLES に登録のあるものをすべて置き換え
            formatted_list.append((sort_key_text, text))  # リストに追加
        except ProfessionalActivity.DoesNotExist:  # 存在しなければスルー．
            pass
    return formatted_list


class ListDownload(LoginRequiredMixin, View):
    """リストダウンロード"""
    
    def get(self, request, *args, **kwargs):
        header = request.session.get('header', False)  # セッションに保存したヘッダを取得
        list_format = json.loads(request.session.get('format', False))  # セッションに保存したフォーマットを取得
        footer = request.session.get('footer', False)  # セッションに保存したフッタを取得
        list_sort_key = json.loads(request.session.get('sort_key', False))  # セッションに保存した並び替えキを取得
        descending_order = request.session.get('descending_order', False)  # セッションに保存した降順かどうかを取得
        extension = request.session.get('extension', False)  # セッションに保存した拡張子を取得
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.%s"' % extension
        response.write(header)  # headerを書き込み
        response.write('\r\n')
        pk_list = request.session.get('pk_list', False)  # セッションに保存したpkのリストを取得
        del request.session['header']
        del request.session['format']
        del request.session['footer']
        del request.session['sort_key']
        del request.session['descending_order']
        del request.session['extension']
        output_list = []
        latex = False
        if extension == 'bib':  # 拡張子がbibの場合
            latex = True
        if 'our_conference_paper' in list_format and 'our_conference_paper' in list_sort_key:
            if 'pk_list' not in request.session:  # pk_listが空なら
                query = OurConferencePaper.objects.values('pk')
                pk_list = [x['pk'] for x in query]
            output_list += our_conference_paper_output_list(list_format['our_conference_paper'],
                                                            list_sort_key['our_conference_paper'],
                                                            pk_list,
                                                            latex)  # フォーマットに従ったリストを得る
        if 'our_int_conf_paper' in list_format \
                and 'our_int_conf_paper' in list_sort_key:
            if 'pk_list' not in request.session:  # pk_listが空なら
                query = OurConferencePaper.objects.values('pk', 'author')
                query_list = []
                for q in query:
                    if not is_japanese(q['author']):  # 日本語でなければ
                        query_list.append(q)
                pk_list = [x['pk'] for x in query_list]
            output_list += our_conference_paper_output_list(list_format['our_int_conf_paper'],
                                                            list_sort_key['our_int_conf_paper'],
                                                            pk_list,
                                                            latex)  # フォーマットに従ったリストを得る
        if 'our_dom_conf_paper' in list_format and 'our_dom_conf_paper' in list_sort_key:
            if 'pk_list' not in request.session:  # pk_listが空なら
                query = OurConferencePaper.objects.values('pk', 'author')
                query_list = []
                for q in query:
                    if is_japanese(q['author']):  # 日本語ならば
                        query_list.append(q)
                pk_list = [x['pk'] for x in query_list]
            output_list += our_conference_paper_output_list(list_format['our_dom_conf_paper'],
                                                            list_sort_key['our_dom_conf_paper'],
                                                            pk_list,
                                                            latex)  # フォーマットに従ったリストを得る
        if 'our_journal_paper' in list_format and 'our_journal_paper' in list_sort_key:
            if 'pk_list' not in request.session:  # pk_listが空なら
                query = OurJournalPaper.objects.values('pk')
                pk_list = [x['pk'] for x in query]
            output_list += our_journal_paper_output_list(list_format['our_journal_paper'],
                                                         list_sort_key['our_journal_paper'],
                                                         pk_list,
                                                         latex)  # フォーマットに従ったリストを得る
        if 'conference_paper' in list_format and 'conference_paper' in list_sort_key:
            if 'pk_list' not in request.session:  # pk_listが空なら
                query = ConferencePaper.objects.values('pk')
                pk_list = [x['pk'] for x in query]
            output_list += conference_paper_output_list(list_format['conference_paper'],
                                                        list_sort_key['conference_paper'],
                                                        pk_list,
                                                        latex)  # フォーマットに従ったリストを得る
        if 'journal_paper' in list_format and 'journal_paper' in list_sort_key:
            if 'pk_list' not in request.session:  # pk_listが空なら
                query = JournalPaper.objects.values('pk')
                pk_list = [x['pk'] for x in query]
            output_list += journal_paper_output_list(list_format['journal_paper'],
                                                     list_sort_key['journal_paper'],
                                                     pk_list,
                                                     latex)  # フォーマットに従ったリストを得る
        if 'url_reference' in list_format and 'url_reference' in list_sort_key:
            if 'pk_list' not in request.session:  # pk_listが空なら
                query = UrlReference.objects.values('pk')
                pk_list = [x['pk'] for x in query]
            output_list += url_reference_output_list(list_format['url_reference'],
                                                     list_sort_key['url_reference'],
                                                     pk_list,
                                                     latex)  # フォーマットに従ったリストを得る
        if 'award' in list_format and 'award' in list_sort_key:
            if 'pk_list' not in request.session:  # pk_listが空なら
                query = Award.objects.values('pk')
                pk_list = [x['pk'] for x in query]
            output_list += award_output_list(list_format['award'],
                                             list_sort_key['award'],
                                             pk_list)  # フォーマットに従ったリストを得る
        if 'activity' in list_format and 'activity' in list_sort_key:
            if 'pk_list' not in request.session:  # pk_listが空なら
                query = ProfessionalActivity.objects.values('pk')
                pk_list = [x['pk'] for x in query]
            output_list += activity_output_list(list_format['activity'],
                                                list_sort_key['activity'],
                                                pk_list)  # フォーマットに従ったリストを得る
        if 'pk_list' in request.session:  # pk_listがあれば
            del request.session['pk_list']
        if len(output_list) == 0:
            return HttpResponseBadRequest(content='400 Bad Request.')  # 一つもなければ400エラー
        if descending_order is True:
            output_list.sort(reverse=True)  # 降順にソート
        else:
            output_list.sort()  # 昇順にソート
        for o in output_list:
            response.write(o[1])  # フォーマットに従ったテキストを書き込み
            response.write('\r\n')
        response.write(footer)  # footerを書き込み
        return response


class FormatFormView(LoginRequiredMixin, FormMixin, TemplateView):
    """フォーマットの入力ページ"""
    form_class = FormatForm
    template_name = 'output/format_form.html'
    
    def get_form_kwargs(self):
        """フォームに渡す変数を追加"""
        kwargs = super(FormatFormView, self).get_form_kwargs()
        if 'format_pk' in self.request.GET:
            kwargs['format_pk'] = self.request.GET['format_pk']
        if 'category' in self.request.GET:
            kwargs['category'] = self.request.GET['category']
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = None
        if 'category' in self.request.GET:
            category = self.request.GET['category']
        if 'format_pk' in self.request.GET:
            format_obj = Format.objects.get(pk=self.request.GET['format_pk'])
            # 変数の説明をテンプレートに渡す
            category = format_obj.category  # format_pkが指定されていればcategoryを上書き
            context['format_pk'] = self.request.GET['format_pk']
        if category == 'our_conference_paper' or category == 'our_int_conf_paper' \
                or category == 'our_dom_conf_paper':
            variables = OurConferencePaper.VARIABLES
        elif category == 'our_journal_paper':
            variables = OurJournalPaper.VARIABLES
        elif category == 'conference_paper':
            variables = ConferencePaper.VARIABLES
        elif category == 'journal_paper':
            variables = JournalPaper.VARIABLES
        elif category == 'url_reference':
            variables = UrlReference.VARIABLES
        elif category == 'award':
            variables = Award.VARIABLES
        elif category == 'activity':
            variables = ProfessionalActivity.VARIABLES
        else:
            variables = {}
        item_list = {}
        for k, v in variables.items():
            item_list[k] = v.__doc__
            context['item_list'] = item_list
        return context
    
    def get(self, request, *args, **kwargs):
        if 'category' in self.request.GET:
            category = self.request.GET['category']
        else:
            category = 'none'
        if 'session_clear' in self.request.GET:
            if self.request.GET['session_clear'] == 'on':
                if 'pk_list' in self.request.session:
                    del self.request.session['pk_list']  # セッションのpk_listをクリア
        response = super().get(self, request, *args, **kwargs)
        pk_list = self.request.session.get('pk_list', False)  # セッションに保存したpkのリストを取得
        url = reverse('output:format_form')
        if pk_list is not False:  # pk_listの指定があればメッセージを表示
            messages.info(self.request,
                          '下記のPrimary Keyのデータが出力対象として指定されています．'
                          'フォーマットを入力して，入力したフォーマットで出力ボタンを押してください．\n'
                          '%s\n'
                          '<a href="%s?category=%s&session_clear=on">キャンセル</a>' % (pk_list, url, category)
                          )
        return response
    
    def post(self, request, *args, **kwargs):
        category = None
        if 'category' in self.request.GET:
            category = self.request.GET['category']
        format_obj = None
        if 'format_pk' in self.request.GET:
            format_obj = Format.objects.get(pk=self.request.GET['format_pk'])
            category = format_obj.category
        if 'update' in request.POST:  # updateボタンなら
            form = self.form_class(request.POST, instance=format_obj)
            if form.is_valid():
                format_obj = form.save(commit=False)
                format_obj.save()
                messages.info(self.request, '"%s" を更新しました．' % format_obj.name)
                return redirect(reverse('output:format_form') + '?format_pk=' + str(format_obj.pk))
            else:
                context = {'form': form}
                return render(request, 'output/format_form.html', context)
        if 'create' in request.POST:  # createボタンなら
            form = self.form_class(request.POST)
            if form.is_valid():
                format_obj = form.save(commit=False)
                format_obj.user = request.user  # 作成ユーザを登録
                format_obj.created_date = timezone.now()  # 作成時刻を登録
                format_obj.save()
                messages.info(self.request, '"%s" を作成しました．' % format_obj.name)
                return redirect(reverse('output:format_form') + '?format_pk=' + str(format_obj.pk))
            else:
                context = {'form': form}
                return render(request, 'output/format_form.html', context)
        request.session['header'] = request.POST['header']
        request.session['format'] = json.dumps({request.POST['category']: request.POST['format']})
        request.session['footer'] = request.POST['footer']
        request.session['sort_key'] = json.dumps({request.POST['category']: request.POST['sort_key']})
        request.session['descending_order'] = False
        request.session['extension'] = request.POST['extension']
        if 'descending_order' in request.POST:
            request.session['descending_order'] = True
        if category == 'our_conference_paper':
            request.session['format'] = json.dumps({'our_conference_paper': request.POST['format']})
            return redirect(reverse('output:list_download'))  # ダウンロードページにリダイレクト
        elif category == 'our_int_conf_paper':
            request.session['format'] = json.dumps({'our_int_conf_paper': request.POST['format']})
            return redirect(reverse('output:list_download'))  # ダウンロードページにリダイレクト
        elif category == 'our_dom_conf_paper':
            request.session['format'] = json.dumps({'our_dom_conf_paper': request.POST['format']})
            return redirect(reverse('output:list_download'))  # ダウンロードページにリダイレクト
        elif category == 'our_journal_paper':
            request.session['format'] = json.dumps({'our_journal_paper': request.POST['format']})
            return redirect(reverse('output:list_download'))  # ダウンロードページにリダイレクト
        if category == 'conference_paper':
            request.session['format'] = json.dumps({'conference_paper': request.POST['format']})
            return redirect(reverse('output:list_download'))  # ダウンロードページにリダイレクト
        elif category == 'journal_paper':
            request.session['format'] = json.dumps({'journal_paper': request.POST['format']})
            return redirect(reverse('output:list_download'))  # ダウンロードページにリダイレクト
        elif category == 'url_reference':
            request.session['format'] = json.dumps({'url_reference': request.POST['format']})
            return redirect(reverse('output:list_download'))  # ダウンロードページにリダイレクト
        elif category == 'award':
            request.session['format'] = json.dumps({'award': request.POST['format']})
            return redirect(reverse('output:list_download'))  # ダウンロードページにリダイレクト
        elif category == 'activity':
            request.session['format'] = json.dumps({'activity': request.POST['format']})
            return redirect(reverse('output:list_download'))  # ダウンロードページにリダイレクト
        else:
            return Http404


class MixFormatFormView(LoginRequiredMixin, TemplateView):
    """複数のクラスからリストを生成するためのフォームページ
    getパラメータでFormatの名前を渡せば，ページを介さず出力ページにリダイレクト．
    getパラメータがない場合は，選択画面になる．
    """
    # ToDo: フォーマットの複数選択フォームを作成
    template_name = 'output/output_base.html'
    
    def get(self, request, *args, **kwargs):
        response = super().get(self, request, *args, **kwargs)
        format_list = dict()
        sort_key_list = dict()
        if 'format1' in self.request.GET:  # getパラメータがあったらFormatを取得
            try:
                format1 = Format.objects.get(name=self.request.GET['format1'])
            except Format.DoesNotExist:
                return response
            format_list[format1.category] = format1.format  # format1のフォーマットを追加
            sort_key_list[format1.category] = format1.sort_key  # format1のソートキーを追加
            if 'format2' in self.request.GET:  # getパラメータがあったらFormatを取得
                try:
                    format2 = Format.objects.get(name=self.request.GET['format2'])
                except Format.DoesNotExist:
                    return response
                format_list[format2.category] = format2.format  # format1のフォーマットを追加
                sort_key_list[format2.category] = format2.sort_key  # format1のソートキーを追加
            if 'format3' in self.request.GET:  # getパラメータがあったらFormatを取得
                try:
                    format3 = Format.objects.get(name=self.request.GET['format3'])
                except Format.DoesNotExist:
                    return response
                format_list[format3.category] = format3.format  # format1のフォーマットを追加
                sort_key_list[format3.category] = format3.sort_key  # format1のソートキーを追加
            request.session['header'] = format1.header  # format1のヘッダ
            request.session['format'] = json.dumps(format_list)  # json化してセッションに保存
            request.session['footer'] = format1.footer  # format1のフッタ
            request.session['sort_key'] = json.dumps(sort_key_list)  # json化してセッションに保存
            request.session['descending_order'] = False
            request.session['extension'] = format1.extension  # format1の拡張子
            if format1.descending_order is True:  # format1の基準でソート
                request.session['descending_order'] = True
            return redirect(reverse('output:list_download'))  # ダウンロードページにリダイレクト
        else:
            return response
