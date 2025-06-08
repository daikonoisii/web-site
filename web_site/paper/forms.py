# -*- coding: utf-8 -*-
from django import forms
from django.forms import Form, ModelForm
from .models import JournalPaper, JournalTitle, OurJournalPaper, ConferencePaper, OurConferencePaper, ConferenceTitle, UrlReference
from users.models import User
from django.urls import reverse


class SearchForm(Form):
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


class JournalPaperForm(ModelForm):
    """論文誌論文のモデルフォーム"""
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        queryset = User.objects.filter(pk=user.pk)
        super().__init__(*args, **kwargs)
        self.fields['citation_key'].widget = forms.TextInput(
            attrs={'readonly': True,
                   'class': "form-control", }
        )
        self.fields['title'].widget = forms.TextInput(
            attrs={'placeholder': 'Percolation and Epidemic Thresholds in Clustered Networks',
                   'class': "form-control", }
        )
        self.fields['author'].widget = forms.Textarea(
            attrs={'placeholder': 'M. Ángeles Serrano\nMarián Boguñá',
                   'class': "form-control", }
        )
        self.fields['journal_title'].widget = forms.Select(
            attrs={'class': 'chosen-select form-control'}
        )
        self.fields['volume'].widget = forms.TextInput(
            attrs={'placeholder': '97',
                   'class': "form-control", }
        )
        self.fields['number'].widget = forms.TextInput(
            attrs={'placeholder': '8',
                   'class': "form-control", }
        )
        self.fields['year'].widget = forms.NumberInput(
            attrs={'class': "form-control", }
        )
        self.fields['page'].widget = forms.TextInput(
            attrs={'placeholder': '1-4',
                   'class': "form-control", }
        )
        self.fields['abstract'].widget = forms.Textarea(
            attrs={'placeholder': '簡単なメモを入力してください．',
                   'class': "form-control", }
        )
        self.fields['pdf'].widget = forms.FileInput()
        self.fields['user'].widget = forms.Select(
            attrs={'null': False}
        )
        self.fields['created_date'].widget = forms.TextInput(
            attrs={'readonly': True,
                   'placeholder': '自動入力されます',
                   'class': "form-control", }
        )
        self.fields['journal_title'].queryset = JournalTitle.objects.all().order_by('name')  # 論文誌の順番を並び替え
        self.fields['citation_key'].initial = 'undefined'  # citation_keyに一時的に設定
        self.fields['user'].empty_label = None  # --------- の選択肢を削除
        self.fields['user'].initial = user  # 登録ユーザを指定
        self.fields['user'].queryset = queryset  # 登録ユーザのみを選択肢に
    
    def save(self, commit=True):
        self.instance.assign_citation_key()  # 引用コードを自動追加
        self.instance.title_capitalize(self.instance.title)  # タイトルのキャピタライズを自動調整
        obj = super(JournalPaperForm, self).save(commit=commit)
        return obj
    
    class Meta:
        model = JournalPaper
        fields = ('citation_key',
                  'journal_title',
                  'volume',
                  'number',
                  'year',
                  'month',
                  'page',
                  'title',
                  'author',
                  'abstract',
                  'tag',
                  'pdf',
                  'user',
                  'created_date', )
        widgets = {
            'tag': forms.SelectMultiple(
                attrs={'class': 'chosen-select form-control'}
            ),
            'month': forms.Select(
                attrs={'class': "form-control", }
            )
        }  # 何故かinitに書くとうまく機能しない


class OurJournalPaperForm(JournalPaperForm):
    """研究室内の論文誌論文のモデルフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['post_print'].widget = forms.FileInput()
        self.fields['pre_print'].widget = forms.FileInput()
        self.fields['published_date'].widget = forms.SelectDateWidget(
            years=[x for x in range(2000, 2050)],
            months={
                1: '1', 2: '2', 3: '3', 4: '4',
                5: '5', 6: '6', 7: '7', 8: '8',
                9: '9', 10: '10', 11: '11', 12: '12'
            },
            attrs={}
        )
        self.fields['letter'].widget = forms.CheckboxInput()
        self.fields['invited'].widget = forms.CheckboxInput()
        self.fields['year'].required = False  # yearを一時的に必須から解除
        self.fields['year'].widget = forms.HiddenInput()  # 年は表示しない
        self.fields['month'].widget = forms.HiddenInput()  # 月は表示しない
        self.fields['doi'].widget = forms.TextInput(
            attrs={'placeholder': '10.1109/TIT.2016.2636847',
                   'class': "form-control", }
        )
        self.fields['url'].widget = forms.TextInput(
            attrs={'placeholder': 'https://ieeexplore.ieee.org/document/8526826',
                   'class': "form-control", }
        )
        self.fields['fwci'].widget = forms.NumberInput(
            attrs={'readonly': True,
                   'placeholder': '自動入力されます',
                   'class': "form-control", }
        )
        self.fields['scopus_cite'].widget = forms.NumberInput(
            attrs={'readonly': True,
                   'placeholder': '自動入力されます',
                   'class': "form-control", }
        )
    
    def save(self, commit=True):
        self.instance.assign_citation_key()  # 引用コードを自動追加
        self.instance.year = self.instance.published_date.year
        self.instance.month = self.instance.published_date.month
        obj = super(OurJournalPaperForm, self).save(commit=commit)
        return obj
    
    class Meta(JournalPaperForm.Meta):
        model = OurJournalPaper
        fields = ('citation_key',
                  'journal_title',
                  'volume',
                  'number',
                  'year',
                  'month',
                  'published_date',
                  'page',
                  'title',
                  'author',
                  'author_user',
                  'letter',
                  'invited',
                  'abstract',
                  'tag',
                  'pdf',
                  'post_print',
                  'pre_print',
                  'doi',
                  'url',
                  'fwci',
                  'scopus_cite',
                  'user',
                  'created_date',)
        widgets = {
            'tag': forms.SelectMultiple(
                attrs={'class': 'chosen-select form-control'}
            ),
            'author_user': forms.SelectMultiple(
                attrs={'class': 'chosen-select form-control'},
            ),
        }  # 何故かinitに書くとうまく機能しない


class JournalTitleForm(ModelForm):
    """論文誌名のモデルフォーム"""
    
    class Meta:
        model = JournalTitle
        fields = ('name', 'publisher', 'impact_factor', 'cite_score', 'highest_percentile', 'snip')
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'publisher': forms.TextInput(
                attrs={'class': 'form-control'},
            ),
            'impact_factor': forms.Textarea(
                attrs={'readonly': True,
                       'placeholder': '自動入力されます',
                       'class': "form-control", }
            ),
            'cite_score': forms.Textarea(
                attrs={'readonly': True,
                       'placeholder': '自動入力されます',
                       'class': "form-control", }
            ),
            'highest_percentile': forms.Textarea(
                attrs={'readonly': True,
                       'placeholder': '自動入力されます',
                       'class': "form-control", }
            ),
            'snip': forms.Textarea(
                attrs={'readonly': True,
                       'placeholder': '自動入力されます',
                       'class': "form-control", }
            ),
        }


class ConferencePaperForm(ModelForm):
    """会議論文のモデルフォーム"""
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        queryset = User.objects.filter(pk=user.pk)
        super().__init__(*args, **kwargs)
        self.fields['citation_key'].widget = forms.TextInput(
            attrs={'readonly': True,
                   'class': "form-control", }
        )
        self.fields['title'].widget = forms.TextInput(
            attrs={'placeholder': 'High Precision Active Probing for Internet Measurement',
                   'class': "form-control", }
        )
        self.fields['author'].widget = forms.Textarea(
            attrs={'placeholder': 'Attila Pásztor\nDarryl Veitch',
                   'class': "form-control", }
        )
        self.fields['conference_title'].widget = forms.Select(
            attrs={'class': 'chosen-select form-control'}
        )
        self.fields['presentation_id'].widget = forms.TextInput(
            attrs={'class': "form-control", }
        )
        self.fields['page'].widget = forms.TextInput(
            attrs={'placeholder': '20-31',
                   'class': "form-control", }
        )
        self.fields['abstract'].widget = forms.Textarea(
            attrs={'placeholder': '簡単なメモを入力してください．',
                   'class': "form-control", }
        )
        self.fields['pdf'].widget = forms.FileInput()
        self.fields['user'].widget = forms.Select(
            attrs={'null': False}
        )
        self.fields['created_date'].widget = forms.TextInput(
            attrs={'readonly': True,
                   'placeholder': '自動入力されます',
                   'class': "form-control", }
        )
        self.fields['conference_title'].queryset = ConferenceTitle.objects.all().order_by('name')  # 論文誌の順番を並び替え
        self.fields['citation_key'].initial = 'undefined'  # citation_keyに一時的に設定
        self.fields['user'].empty_label = None  # --------- の選択肢を削除
        self.fields['user'].initial = user  # 登録ユーザを指定
        self.fields['user'].queryset = queryset  # 登録ユーザのみを選択肢に
    
    def save(self, commit=True):
        self.instance.assign_citation_key()  # 引用コードを自動追加
        obj = super(ConferencePaperForm, self).save(commit=commit)
        return obj
    
    class Meta:
        model = ConferencePaper
        fields = ('citation_key',
                  'conference_title',
                  'presentation_id',
                  'page',
                  'title',
                  'author',
                  'abstract',
                  'tag',
                  'pdf',
                  'user',
                  'created_date',)
        widgets = {
            'tag': forms.SelectMultiple(
                attrs={'class': 'chosen-select form-control'}
            ),
            'month': forms.Select(
                attrs={'class': "form-control", }
            )
        }  # 何故かinitに書くとうまく機能しない


class OurConferencePaperForm(ConferencePaperForm):
    """研究室内の会議論文のモデルフォーム"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['post_print'].widget = forms.FileInput()
        self.fields['pre_print'].widget = forms.FileInput()
        self.fields['presentation_pdf'].widget = forms.FileInput()
        self.fields['published_date'].widget = forms.SelectDateWidget(
            years=[x for x in range(2000, 2050)],
            months={
                1: '1', 2: '2', 3: '3', 4: '4',
                5: '5', 6: '6', 7: '7', 8: '8',
                9: '9', 10: '10', 11: '11', 12: '12'
            },
            attrs={}
        )
        self.fields['presenter'].widget = forms.TextInput(
            attrs={'placeholder': 'Kohei Watabe',
                   'class': "form-control", }
        )
        self.fields['short_paper'].widget = forms.CheckboxInput()
        self.fields['poster'].widget = forms.CheckboxInput()
        self.fields['invited'].widget = forms.CheckboxInput()
        self.fields['doi'].widget = forms.TextInput(
            attrs={'placeholder': '10.1109/TIT.2016.2636847',
                   'class': "form-control", }
        )
        self.fields['url'].widget = forms.TextInput(
            attrs={'placeholder': 'https://ieeexplore.ieee.org/document/8526826',
                   'class': "form-control", }
        )
        self.fields['fwci'].widget = forms.NumberInput(
            attrs={'readonly': True,
                   'placeholder': '自動入力されます',
                   'class': "form-control", }
        )
        self.fields['scopus_cite'].widget = forms.NumberInput(
            attrs={'readonly': True,
                   'placeholder': '自動入力されます',
                   'class': "form-control", }
        )
        self.fields['core_rank'].widget = forms.TextInput(
            attrs={'placeholder': 'A*',
                   'class': "form-control", }
        )
    
    def save(self, commit=True):
        self.instance.assign_citation_key()  # 引用コードを自動追加
        obj = super(OurConferencePaperForm, self).save(commit=commit)
        return obj
    
    class Meta(ConferencePaperForm.Meta):
        model = OurConferencePaper
        fields = ('citation_key',
                  'conference_title',
                  'presentation_id',
                  'published_date',
                  'page',
                  'title',
                  'author',
                  'author_user',
                  'presenter',
                  'short_paper',
                  'poster',
                  'invited',
                  'abstract',
                  'subject',
                  'tag',
                  'pdf',
                  'post_print',
                  'pre_print',
                  'presentation_pdf',
                  'doi',
                  'url',
                  'fwci',
                  'scopus_cite',
                  'core_rank',
                  'user',
                  'created_date',)
        widgets = {
            'tag': forms.SelectMultiple(
                attrs={'class': 'chosen-select form-control'}
            ),
            'subject': forms.SelectMultiple(
                attrs={'class': 'chosen-select form-control'}
            ),
            'author_user': forms.SelectMultiple(
                attrs={'class': 'chosen-select form-control'},
            ),
        }  # 何故かinitに書くとうまく機能しない


class ConferenceTitleForm(ModelForm):
    """国際会議名のモデルフォーム"""
    
    class Meta:
        model = ConferenceTitle
        fields = ('name', 'year', 'month', 'venue', 'country', 'organizer', 'cite_score', 'highest_percentile', 'snip',
                  'acceptance_ratio')
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': 'The 15th Annual International Conference on '
                                      'Mobile Computing and Networking (MobiCom 2009) Workshop',
                       'class': 'form-control'}
            ),
            'year': forms.NumberInput(
                attrs={'placeholder': '2009',
                       'class': 'form-control'},
            ),
            'month': forms.Select(
                attrs={'class': 'form-control'},
            ),
            'venue': forms.TextInput(
                attrs={'placeholder': 'Miami',
                       'class': 'form-control'},
            ),
            'country': forms.TextInput(
                attrs={'placeholder': 'FL, USA',
                       'class': 'form-control'},
            ),
            'organizer': forms.TextInput(
                attrs={'placeholder': 'IEEE',
                       'class': 'form-control'},
            ),
            'cite_score': forms.Textarea(
                attrs={'readonly': True,
                       'placeholder': '自動入力されます',
                       'class': "form-control", }
            ),
            'highest_percentile': forms.Textarea(
                attrs={'readonly': True,
                       'placeholder': '自動入力されます',
                       'class': "form-control", }
            ),
            'snip': forms.NumberInput(
                attrs={'readonly': True,
                       'placeholder': '自動入力されます',
                       'class': "form-control", }
            ),
            'acceptance_ratio': forms.NumberInput(
                attrs={'placeholder': '0.232',
                       'class': "form-control", }
            ),
        }


class UrlReferenceForm(ModelForm):
    """URLのモデルフォーム"""

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        queryset = User.objects.filter(pk=user.pk)
        super().__init__(*args, **kwargs)
        self.fields['citation_key'].widget = forms.TextInput(
            attrs={'placeholder': 'Internet2',
                   'class': "form-control", }
        )
        self.fields['title'].widget = forms.TextInput(
            attrs={'placeholder': 'Internet2 Network NOC',
                   'class': "form-control", }
        )
        self.fields['url'].widget = forms.TextInput(
            attrs={'placeholder': 'https://docs.globalnoc.iu.edu/i2network/',
                   'class': "form-control", }
        )
        self.fields['pdf'].required = True  # urlの場合は保存性の観点からPDFを必須に
        self.fields['pdf'].widget = forms.FileInput()
        self.fields['created_date'].widget = forms.TextInput(
            attrs={'readonly': True,
                   'placeholder': '自動入力されます',
                   'class': "form-control", }
        )
        self.fields['user'].empty_label = None  # --------- の選択肢を削除
        self.fields['user'].initial = user  # 登録ユーザを指定
        self.fields['user'].queryset = queryset  # 登録ユーザのみを選択肢に

    def save(self, commit=True):
        self.instance.title_capitalize(self.instance.title)  # タイトルのキャピタライズを自動調整
        obj = super(UrlReferenceForm, self).save(commit=commit)
        return obj

    class Meta:
        model = UrlReference
        fields = ('citation_key',
                  'title',
                  'tag',
                  'url',
                  'pdf',
                  'user',
                  'created_date',)
        widgets = {
            'tag': forms.SelectMultiple(
                attrs={'class': 'chosen-select form-control'}
            ),
        }  # 何故かinitに書くとうまく機能しない
