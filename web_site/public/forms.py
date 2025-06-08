# -*- coding: utf-8 -*-
from django import forms
from django.forms import Form


class ExamForm(Form):
    student_id = forms.CharField(
        label='学籍番号',
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': '',
                'class': "",
            },
        ),
        help_text='学籍番号を入力してください．'
    )
