from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from picture.models import Picture
from datetime import timedelta


class Information(models.Model):
    date = models.DateField(verbose_name='年月日')
    description = models.TextField('説明')
    e_description = models.TextField('説明(英語)', null=True, default=None)
    picture = models.ForeignKey(
        Picture,
        null=True,
        blank=True,
        related_name='information_picture',
        on_delete=models.CASCADE,
        verbose_name='画像',
        help_text='関連する画像があれば登録してください．'
    )
    
    def is_new(self):
        """14日以内の新しい情報かどうか判定"""
        return self.date > timezone.now().date() - timedelta(days=14)
    
    def __str__(self):
        return str(self.date)


class Research(models.Model):
    title = models.CharField('タイトル', unique=True, max_length=20)
    e_title = models.CharField('タイトル(英語)', max_length=40, blank=True)
    icon_tag = models.CharField('アイコンタグ', max_length=50)
    description = models.TextField('説明')
    e_description = models.TextField('説明(英語)', blank=True)
    weight = models.IntegerField('優先順位',
                                 default=5,
                                 validators=[MinValueValidator(0, message='0より小さい値は入力できません．'),
                                             MaxValueValidator(9, message='9より大きい値は入力できません．')],
                                 help_text='表示順を決める優先順位を入力してください(0-9)．')
    
    def __str__(self):
        return str(self.title)


class Skill(models.Model):
    name = models.CharField('キーワード', unique=True, max_length=20)
    weight = models.IntegerField('ウエイト',
                                 validators=[MinValueValidator(0, message='0より小さい値は入力できません．'),
                                             MaxValueValidator(9, message='9より大きい値は入力できません．')],
                                 help_text='表示サイズを決めるウエイトを入力してください(0-9)．')
    
    def __str__(self):
        return str(self.name)


class Internship(models.Model):
    name = models.CharField('派遣先名', unique=True, max_length=20)
    weight = models.IntegerField('優先順位',
                                 validators=[MinValueValidator(0, message='0より小さい値は入力できません．'),
                                             MaxValueValidator(9, message='9より大きい値は入力できません．')],
                                 help_text='表示順を決める優先順位を入力してください(0〜9)．')
    
    def __str__(self):
        return str(self.name)


class QAndA(models.Model):
    question = models.TextField('質問内容', help_text='質問内容を入力してください．')
    answer = models.TextField('回答内容', help_text='回答内容を入力してください．')
    weight = models.IntegerField('優先順位',
                                 validators=[MinValueValidator(0, message='0より小さい値は入力できません．'),
                                             MaxValueValidator(9, message='9より大きい値は入力できません．')],
                                 help_text='表示順を決める優先順位を入力してください(0〜9)．')
    
    def __str__(self):
        return str(self.question)


class Schedule(models.Model):
    name = models.CharField('イベント', max_length=40)
    month = models.IntegerField('実施月',
                                validators=[MinValueValidator(1, message='1より小さい値は入力できません．'),
                                            MaxValueValidator(12, message='12より大きい値は入力できません．')],
                                help_text='イベントを実施する付きを入力してください(1〜12)．')
    weight = models.IntegerField('優先順位',
                                 blank=True,
                                 validators=[MinValueValidator(0, message='0より小さい値は入力できません．'),
                                             MaxValueValidator(9, message='9より大きい値は入力できません．')],
                                 default=5,
                                 help_text='同じ月の実施イベントの中での表示の優先順位を入力してください(0〜9)．')
    
    def __str__(self):
        return str(self.name)
