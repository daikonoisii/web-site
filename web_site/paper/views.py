from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from .models import Reference, JournalPaper, ConferencePaper, OurJournalPaper, OurConferencePaper, \
    JournalTitle, ConferenceTitle, UrlReference
from .forms import SearchForm, JournalPaperForm, OurJournalPaperForm, JournalTitleForm, \
    ConferencePaperForm, OurConferencePaperForm, ConferenceTitleForm, UrlReferenceForm
from django.db.models import Q
from django.http import FileResponse, Http404, JsonResponse
from lib.japanese import is_japanese
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from web_site.settings import BASE_DIR
# from decimal import *
import io
import os
import hashlib
from datetime import datetime


def get_paper_type(pk):
    """Referenceのpkから，継承しているオブジェクトを見つける関数"""
    try:  # 継承しているオブジェクトを見つける
        inherit_obj = OurJournalPaper.objects.get(pk=pk)
        paper_type = 'our_journal'
        return inherit_obj, paper_type  # 継承したオブジェクトとタイプを返す
    except OurJournalPaper.DoesNotExist:
        pass
    try:  # 継承しているオブジェクトを見つける
        inherit_obj = OurConferencePaper.objects.get(pk=pk)
        paper_type = 'our_conference'
        return inherit_obj, paper_type  # 継承したオブジェクトとタイプを返す
    except OurConferencePaper.DoesNotExist:
        pass
    try:  # 継承しているオブジェクトを見つける
        inherit_obj = JournalPaper.objects.get(pk=pk)
        paper_type = 'journal'
        return inherit_obj, paper_type  # 継承したオブジェクトとタイプを返す
    except JournalPaper.DoesNotExist:
        pass
    try:  # 継承しているオブジェクトを見つける
        inherit_obj = ConferencePaper.objects.get(pk=pk)
        paper_type = 'conference'
        return inherit_obj, paper_type  # 継承したオブジェクトとタイプを返す
    except ConferencePaper.DoesNotExist:
        pass
    try:  # 継承しているオブジェクトを見つける
        inherit_obj = UrlReference.objects.get(pk=pk)
        paper_type = 'url_reference'
        return inherit_obj, paper_type  # 継承したオブジェクトとタイプを返す
    except UrlReference.DoesNotExist:
        return None, None  # なければNoneを返す


class PaperTop(LoginRequiredMixin, ListView):
    """業績・文献管理トップページ表示"""
    model = Reference
    context_object_name = 'papers'
    template_name = 'paper/paper_top.html'
    
    def get_queryset(self):
        release_period = timezone.now().date() - timezone.timedelta(days=14)
        return Reference.objects.filter(
            created_date__range=(release_period, timezone.datetime.now())
        ).order_by('-created_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new'] = timezone.now().date()
        context['past'] = timezone.now().date() - timezone.timedelta(days=14)
        return context


class PaperDetail(LoginRequiredMixin, DetailView):
    """論文のpdf表示"""
    model = Reference
    template_name = 'paper/paper_detail.html'
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        reference_obj = kwargs['object']
        inherit_obj, paper_type = get_paper_type(reference_obj.pk)  # 継承しているオブジェクトを取る
        if paper_type != 'url_reference':
            author = inherit_obj.comma_author()
        else:  # url_referenceの場合は著者なし
            author = None
        related_reports = reference_obj.related_paper.all()  # 関連するレポートを取得
        context = super(PaperDetail, self).get_context_data(**kwargs)
        context.update({'url_prefix': settings.URL_PREFIX,
                        'paper_type': paper_type,
                        'inherit_obj': inherit_obj,
                        'author': author,
                        'related_reports': related_reports})  # contextで渡すデータを追加
        return context


class PaperPdfView(LoginRequiredMixin, View):
    """PDF表示"""
    def get(self, request, *args, **kwargs):
        paper = Reference.objects.get(pk=kwargs['pk'])
        if paper is None:
            raise Http404  # レポートがなければ404エラー
        try:
            response = FileResponse(open(paper.pdf.path, 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            raise Http404  # レポートがなければ404エラー
        response['Content-Disposition'] = 'filename={}.pdf'.format(paper.citation_key)
        return response


def add_text_to_pdf(infile, outfile, text):
    """PDFにテキストを挿入する関数"""
    packet = io.BytesIO()
    # 既存のPDF読み込み
    existing_pdf = PdfFileReader(open(infile, "rb"))
    output = PdfFileWriter()
    (paper_width, paper_height) = existing_pdf.getPage(0).mediaBox.upperRight
    # Reportlab で文字を書き込んだ新しいPDF生成
    can = canvas.Canvas(packet, pagesize=letter)
    x_margin = 10.0  # 文字のマージン
    y_margin = 3.0  # 文字のマージン
    message_style = ParagraphStyle('Normal')
    message_style.fontSize = 6  # 文字サイズ
    message_style.backColor = 'white'  # 背景色
    message_style.fontName = 'Times-Roman'  # フォント
    message_style.leading = 6  # 改行幅
    message = Paragraph(text, style=message_style)
    w, h = message.wrap(float(paper_width) - x_margin * 2, 300)  # 文章エリアのサイズ
    message.drawOn(can, 0 + x_margin, float(paper_height) - y_margin - h)
    # can.drawString(upper_left[0] + x_margin, upper_left[1] - text_size - y_margin, text)
    can.save()
    # move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # ページ0に重ねる
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # 2ページ以降を追加
    for i in range(1, existing_pdf.numPages):
        output.addPage(existing_pdf.getPage(i))
    # ファイルを書き出し
    output_stream = open(outfile, 'wb')
    output.write(output_stream)
    output_stream.close()


class PostPrintView(View):
    """Post-prilt PDF表示"""
    
    @staticmethod
    def copyright_text(organization, author, title, publish_in, year, url, doi):
        """post-printのPDFに追加するテキストを返す関数"""
        text = ''
        if organization == 'IEEE' \
                or organization == 'IEEE Computer Society' \
                or organization == 'IEEE Communication Society':
            args = [author, title, publish_in, year, url, doi]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the post-print version of the following article: ' \
                    '{author}, ``{title},\'\' in {publish_in}, {year}. ' \
                    'The original publication is available at {url} ' \
                    '(DOI: {doi}). ' \
                    '(c) {year} IEEE. Personal use of this material is permitted. ' \
                    'Permission from IEEE must be obtained for all other users, including reprinting/republishing ' \
                    'this material for advertising or promotional purposes, creating new collective works for resale ' \
                    'or redistribution to servers or lists, or reuse of any copyrighted components of this work ' \
                    'in other works. '.format(author=author, title=title, publish_in=publish_in, year=year, url=url,
                                              doi=doi)
        elif organization == 'ACM':
            args = [author, title, publish_in, year, url, doi]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the post-print version of the following article: ' \
                    '{author}, ``{title},\'\' in {publish_in}, {year}. ' \
                    '(c) ACM, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of ACM for your personal use. Not for redistribution. ' \
                    'The definitive version was published in {url} (DOI: {doi}).'.format(author=author, title=title,
                                                                                         publish_in=publish_in,
                                                                                         year=year, url=url, doi=doi)
        elif organization == 'Elsevier':
            args = [year, url, doi]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the post-print version. ' \
                    'The original publication is available at {url} ' \
                    '(DOI: {doi}). ' \
                    '(c) Elsevier, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of Elsevier for your personal use. ' \
                    'Not for redistribution. '.format(year=year, url=url, doi=doi)
        elif organization == 'Springer':
            args = [year, url, doi]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the post-print version. ' \
                    'The original publication is available at {url} ' \
                    '(DOI: {doi}). ' \
                    '(c) Springer, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of Springer for your personal use. ' \
                    'Not for redistribution. '.format(year=year, url=url, doi=doi)
        elif organization == 'IEICE':
            text += ''
        elif organization == 'IFIP':
            args = [year, publish_in]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the post-print version. ' \
                    'The original publication is available at {url}. ' \
                    '(c) IFIP, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of IFIP for your personal use. ' \
                    'Not for redistribution. ' \
                    'The definitive version was ' \
                    'published in {publish_in}. '.format(year=year, publish_in=publish_in, url=url)
        elif organization == 'ORJS':
            args = [year, publish_in]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the post-print version. ' \
                    'The original publication is available at {url}. ' \
                    '(c) ORJS, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of ORJS for your personal use. ' \
                    'Not for redistribution. ' \
                    'The definitive version was ' \
                    'published in {publish_in}. '.format(year=year, publish_in=publish_in, url=url)
        elif organization == 'Taylor & Francis':
            args = [year, publish_in, doi]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is an Accepted Manuscript of an article published by Taylor & Francis' \
                    ' in {publish_in} on {year}, ' \
                    'available at http://wwww.tandfonline.com/{doi} .'.format(year=year, publish_in=publish_in, doi=doi)
        elif organization == 'Willey':
            args = [author, title, publish_in, year, doi]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            if year + 2 > datetime.now().year:
                return None  # 基本24ヶ月以内は公開不可なので，ラフに計算してNoneを返す
            text += 'This is the peer reviewed version of the following article: ' \
                    '{author}, ``{title},\'\' in {publish_in}, {year}. ' \
                    'which has been published in final form at https://doi.org/{doi}. ' \
                    'This article may be used for non-commercial purposes in accordance with Wiley Terms and Conditions ' \
                    'for Use of Self-Archived Versions. This article may not be enhanced, ' \
                    'enriched or otherwise transformed into a derivative work, ' \
                    'without express permission from Wiley or by statutory rights under applicable legislation. ' \
                    'Copyright notices must not be removed, obscured or modified. ' \
                    'The article must be linked to Wiley’s version of record on Wiley Online Library and any embedding, ' \
                    'framing or otherwise making available the article or pages thereof by third parties from platforms, ' \
                    'services and websites other than Wiley Online Library must be prohibited. '.format(author=author,
                                                                                                        title=title,
                                                                                                        publish_in=publish_in,
                                                                                                        year=year,
                                                                                                        doi=doi)
        else:
            text = None  # 該当がなければ None を返す
        return text
    
    def get(self, request, *args, **kwargs):
        try:
            paper = OurConferencePaper.objects.get(pk=kwargs['pk'])
            author = paper.formed_authors()
            title = paper.title
            year = paper.conference_title.year
            organization = paper.conference_title.organizer
            publish_in = 'Proceedings of ' + paper.uncapitalized_conference_name()
            doi = paper.doi
            url = 'https://doi.org/' + str(doi)
        except OurConferencePaper.DoesNotExist:
            try:
                paper = OurJournalPaper.objects.get(pk=kwargs['pk'])
                author = paper.formed_authors()
                title = paper.title
                year = paper.year
                organization = paper.journal_title.publisher
                publish_in = paper.journal_title.name
                doi = paper.doi
                url = 'https://doi.org/' + str(doi)
            except OurJournalPaper.DoesNotExist:
                raise Http404  # 論文がなければ404エラー
        if paper.pdf_publish():  # PDF版が公開可能なら公開．
            try:
                response = FileResponse(open(paper.pdf.path, 'rb'), content_type='application/pdf')
            except FileNotFoundError:
                raise Http404  # 論文がなければ404エラー
            response['Content-Disposition'] = 'filename={}.pdf'.format(paper.citation_key)
            return response
        if paper.post_print_publish():  # post-printが公開可能なら
            text = PostPrintView.copyright_text(organization=organization, author=author, title=title,
                                                publish_in=publish_in, year=year, url=url, doi=doi)
            if text is None:
                raise Http404  # 追加するテキストがなければ 404エラー
            if text == '':
                response = FileResponse(open(paper.pdf.file.name, 'rb'), content_type='application/pdf')
            else:
                temp_file = 'media/temp/' + hashlib.md5(str(datetime.now()).encode()).hexdigest() + '.pdf'  # 一時ファイル名を決める
                temp_file = os.path.join(BASE_DIR, temp_file)
                try:
                    add_text_to_pdf(paper.post_print.path, temp_file, text)  # テキストを追記したPDFの生成
                    response = FileResponse(open(temp_file, 'rb'), content_type='application/pdf')
                except FileNotFoundError:
                    raise Http404  # 論文がなければ404エラー
                os.remove(temp_file)  # 一時ファイルを削除
            response['Content-Disposition'] = 'filename=post_print_{}.pdf'.format(paper.citation_key)
            return response
        else:
            raise Http404  # 404エラー


class PrePrintView(View):
    """Pre-print PDF表示"""
    
    @staticmethod
    def copyright_text(organization, author, title, publish_in, year, url, doi):
        """pre-printのPDFに追加するテキストを返す関数"""
        text = ''
        if organization == 'IEEE' \
                or organization == 'IEEE Computer Society' \
                or organization == 'IEEE Communication Society':
            text += 'This is the pre-print version. ' \
                    'This work was submitted to the IEEE for possible publication. ' \
                    'Copyright may be transferred without notice, after which this version may no longer be accessible'
        elif organization == 'ACM':
            args = [year]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the pre-print version. ' \
                    'This work was submitted to the ACM for possible publication. ' \
                    '(c) ACM, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of ACM for your personal use. ' \
                    'Not for redistribution. '.format(year=year)
        elif organization == 'Elsevier':
            args = [year]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the pre-print version. ' \
                    'This work was submitted to the Elsevier for possible publication. ' \
                    '(c) Elsevier, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of Elsevier for your personal use. ' \
                    'Not for redistribution. '.format(year=year)
        elif organization == 'Springer':
            args = [year]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the pre-print version. ' \
                    'This work was submitted to the Springer for possible publication. ' \
                    '(c) Springer, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of Springer for your personal use. ' \
                    'Not for redistribution. '.format(year=year)
        elif organization == 'IEICE':
            args = [year]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the pre-print version. ' \
                    'This work was submitted to the IEICE for possible publication. ' \
                    '(c) IEICE, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of IEICE for your personal use. ' \
                    'Not for redistribution. '.format(year=year)
        elif organization == 'IFIP':
            args = [year]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the pre-print version. ' \
                    'This work was submitted to the IFIP for possible publication. ' \
                    '(c) IFIP, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of IFIP for your personal use. ' \
                    'Not for redistribution. '.format(year=year)
        elif organization == 'ORSJ':
            args = [year]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the pre-print version. ' \
                    'This work was submitted to the ORSJ for possible publication. ' \
                    '(c) ORSJ, {year}. This is the author\'s version of the work. ' \
                    'It is posted here by permission of ORSJ for your personal use. ' \
                    'Not for redistribution. '.format(year=year)
        elif organization == 'Taylor & Francis':
            args = [year, publish_in, doi]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is an Original Manuscript of an article published by Taylor & Francis' \
                    ' in {publish_in} on {year}, ' \
                    'available at http://wwww.tandfonline.com/{doi} .'.format(year=year, publish_in=publish_in, doi=doi)
        elif organization == 'Wiley':
            args = [author, title, publish_in, year, doi]  # 使う変数一覧
            if any([a is None for a in args]):
                return None  # 使う変数のうち一つでもNoneがあればNoneを返す
            text += 'This is the pre-peer reviewed version of the following article: ' \
                    '{author}, ``{title},\'\' in {publish_in}, {year}. ' \
                    'which has been published in final form at https://doi.org/{doi} . ' \
                    'This article may be used for non-commercial purposes in accordance ' \
                    'with Wiley Terms and Conditions for Use of Self-Archived Versions.'.format(author=author,
                                                                                                title=title,
                                                                                                publish_in=publish_in,
                                                                                                year=year,
                                                                                                doi=doi)
        else:
            text = None  # 該当がなければ None を返す
        return text
    
    def get(self, request, *args, **kwargs):
        try:
            paper = OurConferencePaper.objects.get(pk=kwargs['pk'])
            author = paper.formed_authors()
            title = paper.title
            year = paper.conference_title.year
            organization = paper.conference_title.organizer
            publish_in = paper.uncapitalized_conference_name()
            doi = paper.doi
            url = 'https://doi.org/' + doi
        except OurConferencePaper.DoesNotExist:
            try:
                paper = OurJournalPaper.objects.get(pk=kwargs['pk'])
                author = paper.formed_authors()
                title = paper.title
                year = paper.year
                organization = paper.journal_title.publisher
                publish_in = paper.journal_title.name
                doi = paper.doi
                url = 'https://doi.org/' + doi
            except OurJournalPaper.DoesNotExist:
                raise Http404  # 論文がなければ404エラー
        if paper.pre_print_publish():  # pre-printが公開可能なら
            text = PrePrintView.copyright_text(organization=organization, author=author, title=title,
                                               publish_in=publish_in, year=year, url=url, doi=doi)
            if text is None:
                raise Http404  # 追加するテキストがなければ 404エラー
            if text == '':
                response = FileResponse(open(paper.pdf.file.name, 'rb'), content_type='application/pdf')
            else:
                temp_file = 'media/temp/' + hashlib.md5(str(datetime.now()).encode()).hexdigest() + '.pdf'  # 一時ファイル名を決める
                temp_file = os.path.join(BASE_DIR, temp_file)
                try:
                    add_text_to_pdf(paper.pre_print.path, temp_file, text)  # テキストを追記したPDFの生成
                    response = FileResponse(open(temp_file, 'rb'), content_type='application/pdf')
                except FileNotFoundError:
                    raise Http404  # 論文がなければ404エラー
                os.remove(temp_file)  # 一時ファイルを削除
            response['Content-Disposition'] = 'filename=pre_print_{}.pdf'.format(paper.citation_key)
            return response
        else:
            raise Http404  # 404エラー


class PresentationPdfView(View):
    """発表資料PDF表示"""
    def get(self, request, *args, **kwargs):
        paper = OurConferencePaper.objects.get(pk=kwargs['pk'])
        if paper is None:
            raise Http404  # レポートがなければ404エラー
        if request.user.is_authenticated is True:
            try:
                response = FileResponse(open(paper.presentation_pdf.path, 'rb'), content_type='application/pdf')
            except FileNotFoundError:
                raise Http404  # レポートがなければ404エラー
        else:
            if paper.presentation_pdf is not None:
                try:
                    response = FileResponse(open(paper.presentation_pdf.path, 'rb'), content_type='application/pdf')
                except FileNotFoundError:
                    raise Http404  # レポートがなければ404エラー
            else:
                raise Http404  # プレゼン用PDFがなく，ログインしていないユーザなら404
        response['Content-Disposition'] = 'filename=presentation_pdf_{}.pdf'.format(paper.citation_key)
        return response


class PaperSearch(LoginRequiredMixin, FormMixin, TemplateView):
    """文献の検索結果表示"""
    form_class = SearchForm
    template_name = 'paper/paper_search.html'


class AjaxPaperSearch(LoginRequiredMixin, View):
    """文献の検索結果をajaxで表示"""
    def get(self, request):
        search = request.GET.get('paper')

        # 論文誌を検索
        if search:
            # 全角スペースを半角スペースに変換して，半角スペースで検索ワードを区切る
            words = search.replace("　"," ").split(" ")

            # 先頭や末尾に 'OR' があれば削除
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

            # queryを作成
            sql_query = Q()
            for word_idx, word in enumerate(words):
                if word_idx in or_idx_list:
                    # 新規 query を`sql_query`に OR で追加する
                    sql_query |= (
                        Q(abstract__icontains=word) |
                        Q(title__icontains=word) |
                        Q(author__icontains=word) |
                        Q(journal_title__name__icontains=word)
                    )
                else:
                    # 新規 query を`sql_query`に AND で追加する
                    sql_query &= (
                        Q(abstract__icontains=word) |
                        Q(title__icontains=word) |
                        Q(author__icontains=word) |
                        Q(journal_title__name__icontains=word)
                    )
            # filter by query
            papers = JournalPaper.objects.filter(sql_query).order_by('-created_date')
        else:
            papers = JournalPaper.objects.all().order_by('-created_date')

        paper_list = []
        for paper in papers:
            related_report = ''
            if len(paper.related_paper.all()) != 0:
                related_report = ' <span class="small_font badge badge-secondary">レポートあり</span>'
            tag = ''
            tag_list = paper.tag.all()
            if len(tag_list) > 0:
                tag = '<strong class="ml-2">タグ:</strong> '
            for t in tag_list:
                tag += '<span class="badge badge-primary">%s</span> ' % t.name
            paper_list.append(
                {
                    'class': 'journal_paper',
                    'label': '論文誌',
                    'pk': paper.pk,
                    'title': paper.title,
                    'tag': tag,
                    'author': paper.formed_authors(),
                    'source': paper.source_text(),
                    'year': paper.year,
                    'related_report': related_report,
                    'abstract': paper.abstract,
                    'created_date': paper.created_date,
                    'user': paper.user.username
                }
            )
        
        # 会議を検索
        if search:
            # 全角スペースを半角スペースに変換して，半角スペースで検索ワードを区切る
            words = search.replace("　"," ").split(" ")
            
            # 先頭や末尾に 'OR' があれば削除
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
            
            # queryを作成
            sql_query = Q()
            for word_idx, word in enumerate(words):
                if word_idx in or_idx_list:
                    # 新規 query を`sql_query`に OR で追加する
                    sql_query |= (
                        Q(abstract__icontains=word) |
                        Q(title__icontains=word) |
                        Q(author__icontains=word) |
                        Q(conference_title__name__icontains=word)
                    )
                else:
                    # 新規 query を`sql_query`に AND で追加する
                    sql_query &= (
                        Q(abstract__icontains=word) |
                        Q(title__icontains=word) |
                        Q(author__icontains=word) |
                        Q(conference_title__name__icontains=word)
                    )

            # filter by query
            papers = ConferencePaper.objects.filter(sql_query).order_by('-created_date')
        else:
            papers = ConferencePaper.objects.all().order_by('-created_date')
        for paper in papers:
            related_report = ''
            if len(paper.related_paper.all()) != 0:
                related_report = ' <span class="small_font badge badge-secondary">レポートあり</span>'
            tag = ''
            tag_list = paper.tag.all()
            if len(tag_list) > 0:
                tag = '<strong class="ml-2">タグ:</strong> '
            for t in tag_list:
                tag += '<span class="badge badge-primary">%s</span> ' % t.name
            if is_japanese(paper.conference_title.name):
                label = '国内会議'
            else:
                label = '国際会議'
                
            paper_list.append(
                {
                    'class': 'conference_paper',
                    'label': label,
                    'pk': paper.pk,
                    'title': paper.title,
                    'tag': tag,
                    'author': paper.formed_authors(),
                    'source': paper.source_text(),
                    'year': paper.conference_title.year,
                    'related_report': related_report,
                    'abstract': paper.abstract,
                    'created_date': paper.created_date,
                    'user': paper.user.username
                }
            )
        
        # URLを検索
        if search:
            # 全角スペースを半角スペースに変換して，半角スペースで検索ワードを区切る
            words = search.replace("　"," ").split(" ")

            # 先頭や末尾に 'OR' があれば削除
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

            # queryを作成
            sql_query = Q()
            for word_idx, word in enumerate(words):
                if word_idx in or_idx_list:
                    # 新規 query を`sql_query`に OR で追加する
                    sql_query |= (
                        Q(abstract__icontains=word) |
                        Q(title__icontains=word) |
                        Q(url__icontains=word)
                    )
                else:
                    # 新規 query を`sql_query`に AND で追加する
                    sql_query &= (
                        Q(abstract__icontains=word) |
                        Q(title__icontains=word) |
                        Q(url__icontains=word)
                    )

            # filter by query
            papers = UrlReference.objects.filter(sql_query).order_by('-created_date')
        else:
            papers = UrlReference.objects.all().order_by('-created_date')
        for paper in papers:
            related_report = ''
            if len(paper.related_paper.all()) != 0:
                related_report = ' <span class="small_font badge badge-secondary">レポートあり</span>'
            tag = ''
            tag_list = paper.tag.all()
            if len(tag_list) > 0:
                tag = '<strong class="ml-2">タグ:</strong> '
            for t in tag_list:
                tag += '<span class="badge badge-primary">%s</span> ' % t.name
            paper_list.append(
                {
                    'class': 'url_reference',
                    'label': 'Web',
                    'pk': paper.pk,
                    'title': paper.title,
                    'tag': tag,
                    'author': '',
                    'source': paper.url,
                    'year': '',
                    'related_report': related_report,
                    'abstract': paper.abstract,
                    'created_date': paper.created_date,
                    'user': paper.user.username
                }
            )
        
        context = {
            'paper_list': paper_list,
        }
        return JsonResponse(context)


class JournalPaperCreate(LoginRequiredMixin, CreateView):
    """論文誌登録ページ"""
    model = JournalPaper
    form_class = JournalPaperForm
    template_name = "paper/paper_edit.html"
    
    def get_form_kwargs(self):
        """フォームに渡す変数を追加"""
        kwargs = super(JournalPaperCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse('paper:paper_detail', kwargs={'pk': self.object.id})  # 成功時にリダイレクトするURL


class JournalPaperUpdate(LoginRequiredMixin, UpdateView):
    """論文誌更新ページ"""
    model = JournalPaper
    form_class = JournalPaperForm
    template_name = "paper/paper_edit.html"
    
    def get_form_kwargs(self):
        """フォームに渡す変数を追加"""
        kwargs = super(JournalPaperUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse('paper:paper_detail', kwargs={'pk': self.object.id})  # 成功時にリダイレクトするURL


class OurJournalPaperCreate(JournalPaperCreate):
    """論文誌論文登録ページ"""
    model = OurJournalPaper
    form_class = OurJournalPaperForm


class OurJournalPaperUpdate(JournalPaperUpdate):
    """論文誌論文更新ページ"""
    model = OurJournalPaper
    form_class = OurJournalPaperForm


class JournalTitleCreate(LoginRequiredMixin, CreateView):
    """論文誌名登録ページ"""
    model = JournalTitle
    form_class = JournalTitleForm
    template_name = "paper/journal_title_edit.html"
    
    def get_success_url(self):
        """成功時にリダイレクトするURL"""
        if 'return_pk' in self.request.GET:  # return_pkパラメータがあれば
            return reverse('paper:update_journal_paper', kwargs={'pk': self.request.GET['return_pk']})  # updateに戻す
        else:
            return reverse('paper:create_journal_paper')  # createに戻す


class JournalTitleUpdate(LoginRequiredMixin, UpdateView):
    """論文誌名更新ページ"""
    model = JournalTitle
    form_class = JournalTitleForm
    template_name = "paper/journal_title_edit.html"
    success_url = settings.URL_PREFIX + '/paper/'


class ConferencePaperCreate(JournalPaperCreate):
    """会議論文登録ページ"""
    model = ConferencePaper
    form_class = ConferencePaperForm


class ConferencePaperUpdate(JournalPaperUpdate):
    """会議論文更新ページ"""
    model = ConferencePaper
    form_class = ConferencePaperForm


class OurConferencePaperCreate(ConferencePaperCreate):
    """研究室内会議論文登録ページ"""
    model = OurConferencePaper
    form_class = OurConferencePaperForm


class OurConferencePaperUpdate(ConferencePaperUpdate):
    """研究室内会議論文更新ページ"""
    model = OurConferencePaper
    form_class = OurConferencePaperForm


class ConferenceTitleCreate(LoginRequiredMixin, CreateView):
    """会議名登録ページ"""
    model = ConferenceTitle
    form_class = ConferenceTitleForm
    template_name = "paper/conference_title_edit.html"
    success_url = settings.URL_PREFIX + '/paper/'


class ConferenceTitleUpdate(LoginRequiredMixin, UpdateView):
    """会議名更新ページ"""
    model = ConferenceTitle
    form_class = ConferenceTitleForm
    template_name = "paper/conference_title_edit.html"
    success_url = settings.URL_PREFIX + '/paper/'


class UrlReferenceCreate(JournalPaperCreate):
    """URL登録ページ"""
    model = UrlReference
    form_class = UrlReferenceForm


class UrlReferenceUpdate(JournalPaperUpdate):
    """URL更新ページ"""
    model = UrlReference
    form_class = UrlReferenceForm


class BibtexHowTo(LoginRequiredMixin, TemplateView):
    """BibTeXの使い方を解説するページ"""
    template_name = 'paper/bibtex_how_to.html'
