# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator, MinLengthValidator
# from django.utils.html import mark_safe
from users.models import User
from paper.models import Reference
from public.models import Research
from datetime import datetime as dt
import os
import re


CATEGORY = (
    (1, 'ゼミ資料'),
    (2, '論文レポート'),
    (6, 'サイドプロジェクト'),
    (9, 'その他'),
)


# -------------------------- #
# upload先のディレクトリ指定 #
# -------------------------------------------------------------------------
# user_path         : ユーザ名のディレクトリ
# time              :
# time_dir_path     : 投稿日のディレクトリ
# user_dir_path     : 最終的なpdf保存先のパス
#
# ex.
# File name  : sample.pdf
# 投稿日     : 2018/10/19
#
# 保存先パス : username/report/category/2018/10/19/sample.pdf
# -------------------------------------------------------------------------
def get_upload_to(instance, filename):
    category_name = instance.get_category_display()
    mapping = {'ゼミ資料': 'seminar',
               '論文レポート': 'paper_report',
               'サイドプロジェクト': 'side_project',
               'その他': 'others'}
    category_dir = mapping[category_name]  # カテゴリ名をディレクトリ名に変更
    user_path = str(instance.user.username)
    time = dt.now()
    time_dir_path = time.strftime('%Y/%m/%d')
    user_dir_path = user_path + "/"\
        + "report" + "/"\
        + category_dir + "/"\
        + time_dir_path

    return os.path.join(str(user_dir_path), filename)


# -------------- #
# レポートモデル #
# ------------------------------------------------------
# title : タイトル
# user         : Userのテーブルとリレーション(1対多)
# abstract     : 概要
# pdf          : ファイル添付用
# created_date : 作成日
# ------------------------------------------------------
class Report(models.Model):
    category = models.IntegerField('カテゴリ', choices=CATEGORY, default=9)
    
    title = models.CharField(
        default='No Title',
        max_length=400,
    )
    
    user = models.ForeignKey(
        User,
        related_name='user_reports',
        on_delete=models.CASCADE,
        null=True,
        default=None
    )
    
    abstract_validator = MinLengthValidator(
        5,
        message="5文字以上入力してください．"
    )
    abstract = models.TextField(validators=[abstract_validator, ])

    pdf_validator = FileExtensionValidator(
        ['pdf', 'txt', 'md'],
        message="ファイル拡張子は *.pdf ，*.md，*.txt としてください．"
    )
    pdf = models.FileField(
        upload_to=get_upload_to,
        verbose_name='添付ファイル',
        validators=[pdf_validator, ],
        help_text='PDF，Markdown，またはテキストファイルを添付してください．'
    )
    paper = models.ForeignKey(
        Reference,
        related_name='related_paper',
        verbose_name='関連論文',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='論文レポートなどで，関連する論文がある場合は登録してください．'
    )
    research = models.ForeignKey(
        Research,
        related_name='related_research',
        verbose_name='関連テーマ',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='研究テーマを説明するためのスライドの場合は，関連するテーマを登録してください．チェックを入れると研究紹介のページに公開されるようになります．'
    )
    created_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='投稿日'
    )
    
    def get_file_type(self):
        """ファイルタイプを返す関数"""
        if re.match(r'^.*\.pdf$', self.pdf.path):  # PDFの場合
            return 'pdf'
        elif re.match(r'^.*\.txt$', self.pdf.path):  # テキストの場合
            return 'txt'
        elif re.match(r'^.*\.md$', self.pdf.path):  # Markdownの場合
            return 'md'
        else:
            return 'unknown'
    
    def __str__(self):
        return str(self.pdf)
    
    class Meta:
        db_table = 'reports'


# -------------- #
# コメントモデル #
# ------------------------------------------------------
# user          : Userのテーブルとリレーション(1対多)
# report        : Reportのテーブルとリレーション(1対多)
# comment       : コメント
# created_date  : 投稿日
# ------------------------------------------------------
class Comment(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_comments',
        on_delete=models.CASCADE
    )

    report = models.ForeignKey(
        Report,
        related_name='report_comments',
        on_delete=models.CASCADE
    )

    comment = models.TextField()

    published_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='投稿日'
    )

    def __str__(self):
        return str(self.published_date)

    class Meta:
        db_table = 'comments'

    # def get_message_as_markdown(self):
    #    return mark_safe(markdown(self.comment, safe_mode='escape'))
