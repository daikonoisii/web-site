# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Form
from paper.models import Reference
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse_lazy
from io import BytesIO
import re


from .models import Report, Comment, CATEGORY


class ReferenceChoiceField(forms.ModelChoiceField):
    """参考文献を選択するフィールド"""
    def label_from_instance(self, obj):
        return u'%s  --  (%s)' % (obj.title, obj.citation_key)


class NewReportForm(ModelForm):
    category = forms.ChoiceField(
        label='カテゴリ',
        widget=forms.Select,
        choices=CATEGORY,
        required=True,
    )
    title = forms.CharField(
        label='タイトル',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'タイトルを入力してください',
                'class': "form-control",
            }),
    )
    abstract = forms.CharField(
        label='概要',
        widget=forms.Textarea(
            attrs={
                'placeholder': '概要を入力してください',
                'class': "form-control",
            }),
    )
    txt = forms.CharField(
        label='本文',
        widget=forms.Textarea(
            attrs={
                'placeholder': '本文を入力してください',
                'class': "form-control",
            }),
        required=False,
    )
    pdf = forms.FileField(
        label='添付ファイル',
        widget=forms.ClearableFileInput(
            attrs={
                'class': ""
            }
        ),
        help_text='レポートのファイルを指定してください．'
                  'PDF，Markdown，テキスト形式のファイルを指定できます．',
    )
    paper = ReferenceChoiceField(
        label='関連論文',
        required = False,
        queryset=Reference.objects.all().order_by('title'),
        widget=forms.Select(
            attrs={
                'class': "w-100 chosen-select"
            }
        ),
        help_text='論文レポートなどで関連する論文がある場合は指定してください．'
                  'リストに存在しない場合は，先に論文を追加してください．',
    )
    
    def clean_pdf(self):
        """バリデーションをオーバーライド"""
        if 'pdf' in self.changed_data:
            if re.match(r'^.*\.md$', self.cleaned_data['pdf'].name):  # Markdownの場合
                opened_file = self.cleaned_data['pdf']  # InMemoryUploadedFileとして登録ファイルを取得
                text = opened_file.read()  # 中身のテキストを読み込む
                script = b'<script src="https://rawcdn.githack.com/oscarmorrison/md-page/master/md-page.js">' \
                         b'</script><noscript>\n'  # Markdownを表示するためのスクリプト
                buffer = BytesIO(script + text)  # スクリプトをテキストの先頭に追加
                data_file = InMemoryUploadedFile(buffer,
                                                 opened_file.field_name,
                                                 opened_file.name,
                                                 'text/markdown',
                                                 buffer.tell(),
                                                 None)  # InMemoryUploadedFile を新しく作る．
                data_file.content_type_extra = opened_file.content_type_extra
                self.cleaned_data['pdf'] = data_file  # cleaned_dataを差し替え
        return self.cleaned_data['pdf']
    
    class Meta:
        model = Report
        fields = ('category', 'title', 'abstract', 'pdf', 'paper')
        template_name = "report/report_report_new.html"


class CommentForm(ModelForm):
    comment = forms.CharField(
        label='コメント',
        widget=forms.Textarea(
              attrs={
                  'placeholder': 'コメントを入力してください',
                  'class': "comment form-control",
                  'rows': 4,
                  'cols': 40,
              }),
    )

    class Meta:
        model = Comment
        fields = ('comment',)
        template_name = "report/report_detail.html"


class SearchForm(Form):
    category = forms.ChoiceField(
        label='カテゴリ',
        widget=forms.Select(
            attrs={
                'class': "custom-select category-select",
            }),
        choices=CATEGORY,
        required=True,
    )
    query = forms.CharField(
        label='検索ワード',
        widget=forms.TextInput(
            attrs={
                'placeholder': '',
                'class': "search-word form-control",
            },
        ),
        help_text='空欄にすると全件表示します．'
    )


class CategorySelectForm(ModelForm):

    category = forms.ChoiceField(
        label='カテゴリ',
        widget=forms.Select(
            attrs={
                'class': "custom-select search-word",
            }),
        choices=CATEGORY,
        required=True,
    )

    class Meta:
        model = Report
        fields = ('category',)
        template_name = "report/report_my_list.html"
