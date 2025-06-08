# -*- coding: utf-8 -*-

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.views.generic import View, ListView, CreateView, TemplateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.db.models import Q
from django.conf import settings
import datetime
import six
import re
from .models import Report, Comment
from users.models import Student, Teacher
from .forms import NewReportForm, CommentForm, SearchForm, CategorySelectForm
from .slack_webhooks import webhook

# Seach Reports ページ表示


class Report_Search_View(LoginRequiredMixin, View):
    form_class = SearchForm

    def get(self, request):
        context = {'form': self.form_class(), }
        return render(
            request,
            'report/report_all_list.html',
            context
        )


# Seach Reports の検索結果表示
class Ajax_Report_Search(LoginRequiredMixin, View):

    def get(self, request):
        search = request.GET.get('report')
        category = request.GET.get('category')
        if search:
            # 全角スペースを半角スペースに変換して，半角スペースで検索ワードを区切る
            words = search.replace("　"," ").split(" ")

            # 先頭や末尾に "OR" があれば削除
            if words[0] == 'OR':
                words.pop(0)
            if words[-1] == 'OR':
                words.pop(-1)

            # OR を適用する単語の位置を記録
            or_idx_list = []
            for word in words:
                if word == 'OR':
                    or_idx_list.append(words.index('OR') - len(or_idx_list))
                    words.remove(word)

            # query を作成
            sql_query = Q()
            for word_idx, word in enumerate(words):
                if word_idx in or_idx_list:
                    # 新規 query を`sql_query`に OR で追加する
                    sql_query |= (
                        Q(abstract__icontains=word, category=category) |
                        Q(title__icontains=word, category=category) |
                        Q(user__username__icontains=word, category=category) |
                        Q(user__first_name__icontains=word, category=category) |
                        Q(user__last_name__icontains=word, category=category)
                    )
                else:
                    # 新規 query を`sql_query`に AND で追加する
                    sql_query &= (
                        Q(abstract__icontains=word, category=category) |
                        Q(title__icontains=word, category=category) |
                        Q(user__username__icontains=word, category=category) |
                        Q(user__first_name__icontains=word, category=category) |
                        Q(user__last_name__icontains=word, category=category)
                    )

            reports = Report.objects.filter(sql_query).order_by('-created_date')

            report_list = [
                {
                    'pk': post.pk,
                    'title_name': post.title,
                    'abstract': post.abstract,
                    'created_date': post.created_date,
                    'user': post.user.username
                } for post in reports
            ]
        else:
            reports = Report.objects.filter(category=category).order_by('-created_date')
            report_list = [
                {
                    'pk': post.pk,
                    'title_name': post.title,
                    'abstract': post.abstract,
                    'created_date': post.created_date,
                    'user': post.user.username
                } for post in reports
            ]

        context = {
            'report_list': report_list,
        }

        return JsonResponse(context)


# 投稿をリスト表示
class ReportsList(LoginRequiredMixin, ListView):
    model = Report
    context_object_name = 'reports'
    template_name = 'report/report_top.html'

    def get_queryset(self):
        release_period = timezone.now().date() - timezone.timedelta(days=14)
        return Report.objects.filter(
            created_date__range=(release_period, timezone.datetime.now())
        ).order_by('-created_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new'] = timezone.now().date()
        context['past'] = timezone.now().date() - timezone.timedelta(days=14)
        return context


# レポートの詳細表示
class ReportDetail(LoginRequiredMixin, View):
    form_class = CommentForm

    def get(self, request, report_id, *args, **kwargs):
        report = Report.objects.get(pk=report_id)
        comment_queryset = Comment.objects.filter(report_id=report_id)
        context = {
            'report_detail': report,
            'form': self.form_class(),
            'file_type': report.get_file_type(),
            'comments': comment_queryset,
            'url_prefix': settings.URL_PREFIX,
        }

        return render(
            request,
            'report/report_detail.html',
            context
        )


class ReportPdfView(View):
    """PDF表示"""

    def get(self, request, *args, **kwargs):
        report = Report.objects.get(pk=kwargs['pk'])
        if report is None:
            raise Http404  # レポートがなければ404エラー
        if request.user.is_authenticated is True or report.research is not None:  # ログインユーザかresearchの割当がないなら表示
            if re.match(r'^.*\.pdf$', report.pdf.path):  # PDFの場合
                try:
                    response = FileResponse(open(report.pdf.path, 'rb'), content_type='application/pdf')
                    response['Content-Disposition'] = 'filename={}.pdf'.format(kwargs['pk'])
                except FileNotFoundError:
                    raise Http404  # レポートがなければ404エラー
            elif re.match(r'^.*\.txt$', report.pdf.path):  # テキストの場合
                try:
                    response = FileResponse(open(report.pdf.path, 'rb'), content_type='text/plain')
                    response['Content-Disposition'] = 'filename={}.txt'.format(kwargs['pk'])
                except FileNotFoundError:
                    raise Http404  # レポートがなければ404エラー
            elif re.match(r'^.*\.md$', report.pdf.path):  # Markdownの場合
                try:
                    response = FileResponse(open(report.pdf.path, 'rb'), content_type='text/html')
                    response['Content-Disposition'] = 'filename={}.md'.format(kwargs['pk'])
                except FileNotFoundError:
                    raise Http404  # レポートがなければ404エラー
            else:
                raise Http404  # ファイル形式が合わなければ404エラー
        else:
            raise Http404  # researchにチェックがなく，ログインしていないユーザなら404
        return response


# コメント投稿
class Ajax_Comment_Post(View):
    form_class = CommentForm

    def post(self, request, report_id, *args, **kwargs):
        form = self.form_class(request.POST)

        report = Report.objects.get(pk=report_id)
        create_user = report.user.username

        if form.is_valid():
            comment = form.save(commit=False)
            comment.report = report
            comment.user = request.user
            comment.save()

            context = {
                'user': comment.user.username,
                'comment': comment.comment,
                'published_date': comment.published_date,
            }

            webhook('コメント', create_user, context['user'], context['comment'])
            return render(
                request,
                'report/ajax_comment.html',
                context
            )


# コメント欄更新
class Ajax_Comment_Update(View):
    form_class = CommentForm

    def post(self, request, report_id, *args, **kwargs):

        comment_queryset = Comment.objects.filter(report_id=report_id)

        context = {
            'comments': comment_queryset
        }

        return render(
            request,
            'report/ajax_comment_update.html',
            context
        )


# レポート投稿関連
class NewReportCreate(LoginRequiredMixin, View):
    form_class = NewReportForm

    def get(self, request, *args, **kwargs):
        context = {
            'form': self.form_class(),
        }
        return render(
            request,
            'report/report_report_new.html',
            context
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            webhook('レポート', request.user.username, request.POST["category"], request.POST["title"], request.POST["abstract"])

            return redirect(reverse('report:top'))

        context = {'form': form}

        return render(
            request,
            'report/report_report_new.html',
            context
        )


# 編集ページ表示
class ReportEdit(LoginRequiredMixin, View):
    raise_exception = True

    form_class = NewReportForm

    def get(self, request, report_id, *args, **kwargs):
        report = get_object_or_404(Report, pk=report_id)

        # markdownの判定
        text = "本文を入力してください"
        is_markdown = False
        is_text = False
        file_extension = report.get_file_type()
        if (file_extension == "md")or(file_extension == "txt"):
            # ファイルを読み込み、文字列に
            opened_file = report.pdf
            text = opened_file.read()
            text = six.text_type(text, "utf-8")
            p = re.compile(r"<[^>]*?>")
            text = p.sub("", text)

        if file_extension=="md":
            is_markdown = True
        if file_extension=="txt":
            is_text = True

        form = self.form_class(
            instance=report,
            initial = {"txt": text}
        )

        context = {
            'form': form,
            'is_markdown': is_markdown,
            'is_text': is_text
        }
        return render(
            request,
            'report/report_report_new.html',
            context
        )

    def post(self, request, report_id, *args, **kwargs):
        report = get_object_or_404(Report, pk=report_id)

        # markdownの判定
        is_text_renew = False
        is_file_exist=list(request.FILES.values())
        file_extension = report.get_file_type()
        if (file_extension == "md")or(file_extension == "txt"):
            # 新しいファイルがアップロードされていない
            if is_file_exist==[]:
                is_text_renew = True
                opened_file = report.pdf
                file_name = str(opened_file).split("/")[-1]
                file_text = request.POST["txt"]

                if file_extension == "md":
                    script = '<script src="https://rawcdn.githack.com/oscarmorrison/md-page/master/md-page.js">' \
                             '</script><noscript>\n'  # Markdownを表示するためのスクリプト
                    file_text = script + file_text  # スクリプトをテキストの先頭に追加
                f = ContentFile(file_text, file_name)

        form = self.form_class(
            request.POST,
            request.FILES,
            instance=report,
        )

        if form.is_valid():
            report = form.save(commit=False)
            report.save()

            if is_text_renew:
                report.pdf.save(file_name, f)

            return redirect(
                reverse(
                    'report:report_detail',
                    kwargs={'report_id': report_id}
                )
            )

        context = {'form': form}
        return render(
            request,
            'report/report_report_new.html',
            context
        )

    def test_func(self):
        report = get_object_or_404(Report, pk=self.kwargs['report_id'])
        return self.request.user.pk == report.user.pk


# レポート削除
class ReportDelete(LoginRequiredMixin, DeleteView):
    model = Report
    template_name = 'report/report_delete.html'
    success_url = reverse_lazy('report:top')


class SubmissionListView(LoginRequiredMixin, TemplateView):
    """日付と投稿者のリストを表示"""
    template_name = "report/report_submission_list.html"

    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(SubmissionListView, self).get_context_data(**kwargs)
        oldest_date = datetime.date.today() - datetime.timedelta(days=365)  # 1年前の日付を取得
        if 'category' in self.request.GET:  # クエリパラメータがある場合の処理
            category = self.request.GET['category']  # クエリパラメータがcategoryを含めば取得
            # 指定のカテゴリのうち，1年前以降のすべてのレポートを取得
            reports = Report.objects.filter(created_date__gt=oldest_date, category=category).order_by('-created_date')
        else:
            reports = Report.objects.filter(created_date__gt=oldest_date).order_by('-created_date')  # 1年前以降のすべてのレポートを取得
        teachers = Teacher.objects.filter(username='kwatabe')
        students = Student.objects.filter(status__lt=30).order_by('-status', 'last_name_kana')  # 学生のリストを取得
        international_students = Student.objects.filter(status = 71)  # 短期留学生
        index = {}  # ユーザ名からカラム番号を返すindex
        table_head = [{'display': False}]  # テーブルヘッダ
        user_list = list(teachers) + list(students) + list(international_students)
        for i, u in enumerate(user_list):
            index[u.username] = i + 1
            if self.request.LANGUAGE_CODE == 'ja':  # 言語が日本語なら日本語に
                u_name = u.get_short_name()
            else:  # それ以外は英語に
                u_name = u.get_short_name_eng()
            table_head.append({'display': True,
                               'u_name': u_name,
                               'post_num': reports.filter(user__username=u.username).count()
                               })  # テーブルのヘッダ(1行目)
        table = []  # テーブルの本体．各セルを {'display': <表示するか否か: T or F>, <+内容に応じて必要な辞書>} で指定．
        row = [{'display': False} for _ in range(len(user_list) + 1)]
        if len(reports) > 0:  # レポートが一つ以上あれば
            current_date = reports[0].created_date.date()  # 現在時刻に最初のレポートの日付を代入
            row[0] = {'display': True, 'content': current_date}
            for r in reports:
                if current_date > r.created_date.date():
                    table.append(row)  # テーブルに行を追加
                    current_date = r.created_date.date()  # 現在の日付を更新
                    row = [{'display': False} for _ in range(len(user_list) + 1)]  # row初期化
                    row[0] = {'display': True, 'content': current_date}
                if r.user.username in index:  # indexにないものは無視
                    if row[index[r.user.username]]['display']:  # すでにファイルがあれば追加
                        row[index[r.user.username]]['pk_list'].append(r.pk)
                    else:
                        row[index[r.user.username]] = {'display': True, 'pk_list': [r.pk]}
            table.append(row)  # テーブルに行を追加
        context.update({'table_head': table_head,
                        'table': table})  # contextで渡すデータを追加
        return context


# My Post Listページ表示
class My_Reports_View(LoginRequiredMixin, View):
    form_class = CategorySelectForm

    def get(self, request, *args, **kwargs):
        context = {
            'form': self.form_class(),
        }
        return render(
            request,
            'report/report_my_list.html',
            context
        )


# My Post Listにレポート表示
class Ajax_My_Reports_View(LoginRequiredMixin, View):

    def get(self, request):
        search = request.GET.get('report')

        if(search):
            report_list = [
                {
                    'pk': post.pk,
                    'title_name': post.title,
                    'abstract': post.abstract,
                    'created_date': post.created_date,
                    'user': post.user.username
                } for post in Report.objects.filter(category=search, user=request.user)
            ]

        else:
            report_list = []

        context = {
            'report_list': report_list,
        }
        return JsonResponse(context)

# markdownプレビュー
class MarkdownPreview(LoginRequiredMixin, View):
    def post(self, request, report_id):
        text = request.POST["txt"]
        script = '<script src="https://rawcdn.githack.com/oscarmorrison/md-page/master/md-page.js">' \
                 '</script><noscript>\n'  # Markdownを表示するためのスクリプト
        text = script + text  # スクリプトをテキストの先頭に追加
        return HttpResponse(text)
