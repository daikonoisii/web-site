from django.db import models
from users.models import User
from django.core.validators import MinValueValidator


class Item(models.Model):
    """販売商品"""

    CATEGORY = (
        ('Beverages', 'ソフトドリンク'),
        ('Alcohol-drinks', 'アルコール飲料'),
        ('Snacks', '食べ物'),
    )
    
    title = models.CharField('商品名', max_length=20)
    price = models.IntegerField('価格', validators=[MinValueValidator(0, message='価格は正の値でなければなりません．'), ])
    category = models.CharField('カテゴリ', choices=CATEGORY, default=None, max_length=20)
    active = models.BooleanField('マーケットに表示', default=True, help_text='非表示にする場合はチェックを外してください．')
    description = models.TextField('商品説明', blank=True)
    user = models.ForeignKey(
        User,
        related_name='user_item',
        on_delete=models.CASCADE,
        verbose_name='管理者',
        help_text='支払先を指定するために，管理者は別途，<a href="/myaccount" target="_blank">アカウント設定</a>から'
                  'Kyash QRコードまたはPayPay IDを登録する必要があります．'
    )  # 管理ユーザ
    
    def __str__(self):
        return str(self.title)
