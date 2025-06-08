from django.db import models
from users.models import User
from django.utils import timezone
import re
import os


def get_upload_to(instance, filename):
    """ファイルのアップロード先を定義"""
    filename = re.sub(r'[\\/:?."<>| ]', '_', filename)  # ファイル名に使えない文字を置き換え
    extension = os.path.splitext(filename)[-1]
    filename = filename + extension
    return os.path.join('picture/', filename)


class Picture(models.Model):
    """写真クラス"""
    CATEGORY = (
        (1, '研究室イベント'),
        (2, '研究室紹介'),
        (6, '飯テロ'),
        (9, 'その他'),
    )

    category = models.IntegerField('カテゴリ', choices=CATEGORY, default=1)
    caption = models.CharField('キャプション',
                               max_length=300,
                               blank=True,
                               null=True,
                               help_text='簡単な説明を入力してください．')
    user = models.ForeignKey(
        User,
        related_name='user_picture',
        on_delete=models.CASCADE,
        verbose_name='登録ユーザ',
        null=True,
    )  # 作成ユーザ
    file = models.ImageField(
        upload_to=get_upload_to,
        verbose_name='添付ファイル',
        help_text='写真のファイルを登録してください．',
    )
    private = models.BooleanField('メンバー限定公開', default=True, help_text='メンバー限定で公開する場合はチェックを入れてください．')
    web = models.BooleanField('研究室ギャラリー公開', default=False, help_text='ウェブサイトの研究室ギャラリーで公開する場合はチェックを入れてください．')
    top_page = models.BooleanField('背景画像',default=False, help_text='ウェブサイトの背景画像として公開する場合はチェックを入れてください.')
    created_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='登録日'
    )
    
    
    def __str__(self):
        return str(self.caption)
