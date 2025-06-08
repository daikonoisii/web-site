# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from .models import Format
from users.models import User


class FormatForm(ModelForm):
    """Formatのモデルフォーム"""
    def __init__(self, *args, **kwargs):
        initial_format = None
        category = None
        if 'category' in kwargs:
            category = kwargs.pop('category')
        format_pk = None
        if 'format_pk' in kwargs:
            format_pk = kwargs.pop('format_pk')
            initial_format = Format.objects.get(pk=format_pk)
        queryset = User.objects.all()
        if 'user' in kwargs:
            user = kwargs.pop('user')
            queryset = User.objects.filter(pk=user.pk)  # 新規登録の場合はログイン中のユーザのみを選択肢に
        super().__init__(*args, **kwargs)
        # 初期値入力
        if format_pk is not None:
            self.fields['name'].initial = initial_format.name
            self.fields['category'].initial = initial_format.category
            self.fields['header'].initial = initial_format.header
            self.fields['format'].initial = initial_format.format
            self.fields['footer'].initial = initial_format.footer
            self.fields['sort_key'].initial = initial_format.sort_key
            self.fields['descending_order'].initial = initial_format.descending_order
            self.fields['extension'].initial = initial_format.extension
            self.fields['user'].initial = initial_format.user
            self.fields['created_date'].initial = initial_format.created_date
            queryset = User.objects.filter(pk=initial_format.user.pk)  # 登録ユーザのみを選択肢に
        else:
            self.fields['category'].initial = category
        self.fields['user'].empty_label = None  # --------- の選択肢を削除
        self.fields['user'].queryset = queryset  # 登録ユーザのみを選択肢に
    
    class Meta:
        model = Format
        fields = ('name',
                  'category',
                  'header',
                  'footer',
                  'format',
                  'sort_key',
                  'descending_order',
                  'extension',
                  'user',
                  'created_date')
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'category': forms.Select(
                attrs={'class': 'form-control'},
            ),
            'header': forms.Textarea(
                attrs={'class': 'form-control'}
            ),
            'footer': forms.Textarea(
                attrs={'class': 'form-control'}
            ),
            'format': forms.Textarea(
                attrs={'class': 'form-control'}
            ),
            'sort_key': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'descending_order': forms.CheckboxInput(),
            'extension': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'user': forms.Select(
                attrs={'readonly': True,
                       'class': "form-control",
                       }
            ),
            'created_date': forms.DateTimeInput(
                attrs={'readonly': True,
                       'class': "form-control", }
            ),
        }
