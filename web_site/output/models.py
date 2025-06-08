from django.db import models
from django.utils import timezone
from users.models import User

CATEGORY_CHOICES = [
    ('our_journal_paper', '研究室内 論文誌論文'),
    ('our_conference_paper', '研究室内 会議発表'),
    ('our_int_conf_paper', '研究室内 国際会議発表'),
    ('our_dom_conf_paper', '研究室内 国内会議発表'),
    ('journal_paper', '論文誌論文'),
    ('conference_paper', '会議発表'),
    ('url_reference', 'ウェブサイト'),
    ('award', '受賞'),
    ('activity', '委員歴'),
]


class Format(models.Model):
    """出力フォーマットクラス"""
    name = models.CharField('フォーマット名', unique=True, max_length=200)
    category = models.CharField(
        verbose_name='出力データ',
        max_length=20,
        default=None,
        choices=CATEGORY_CHOICES,
        help_text='出力対象のデータの種類を入力してください．'
    )
    header = models.TextField('ヘッダ', blank=True, help_text='出力ファイルのヘッダを入力してください．')
    format = models.TextField('出力フォーマット', help_text='データを出力フォーマットを記述してください．')
    footer = models.TextField('フッタ', blank=True, help_text='出力ファイルのフッタを入力してください．')
    sort_key = models.CharField('並び替えキー', blank=True, max_length=200, help_text='並び順の基準にするキーを変数で入力してください')
    descending_order = models.BooleanField('降順', default=None, null=True,
                                               help_text='デフォルトは並び替えキーで昇順に並べます．降順にする場合はチェックを入れてください．')
    extension = models.CharField('拡張子', default='csv', max_length=10, help_text='出力ファイルの拡張子を指定してください．')
    user = models.ForeignKey(
        User,
        related_name='user_format',
        on_delete=models.CASCADE,
        verbose_name='登録ユーザ',
        null=True,
    )
    created_date = models.DateTimeField(default=timezone.now, verbose_name='作成日')
    
    def __str__(self):
        return str(self.name)
