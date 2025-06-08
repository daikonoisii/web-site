from django.db import models
from users.models import User


class Award(models.Model):
    """学生/教員の受賞"""
    title = models.CharField('タイトル', max_length=100)
    winner = models.TextField('受賞者リスト', max_length=200,
                              help_text='受賞者全員を1名ずつ改行して記入してください．賞のタイトルが英語の場合は，受賞者リストも英語で記入してください．')
    user = models.ManyToManyField(User, verbose_name='研究室内受賞者', related_name='awarded_users', default=None)
    org = models.CharField('授与機関', max_length=100)
    date = models.DateField('受賞年月日')
    
    def each_user(self, u):
        """個々の受賞者"""
        if u in self.user.all():
            return str(u.get_full_name())
        else:
            return None
    
    def winners(self):
        """カンマ区切りの受賞者"""
        value = self.winner.replace('\r\n', ', ')
        value = value.replace('\n', ', ')
        value = value.replace('\r', ', ')
        return value
    
    def award_title(self):
        """賞の名称"""
        return str(self.title)
    
    def year(self):
        """受賞年"""
        return str(self.date.year)
    
    def business_year(self):
        """受賞年度"""
        value = self.date.year
        if self.date.month <= 3:
            value -= 1
        return str(value)
    
    def month(self):
        """受賞月"""
        return str(self.date.month)
    
    def zero_month(self):
        """0詰めの受賞月 (例: 01，02，...)"""
        return str(self.date.strftime('%m'))
    
    def day(self):
        """受賞日"""
        return str(self.date.day)
    
    def zero_day(self):
        """0詰めの受賞日 (例: 01，02，...)"""
        return str(self.date.strftime('%d'))
    
    def org_name(self):
        """授与機関"""
        return str(self.org)
    
    # 置き換え文字列と関数の対応
    VARIABLES = {'{{ each_user }}': each_user,
                 '{{ winners }}': winners,
                 '{{ award_title }}': award_title,
                 '{{ year }}': year,
                 '{{ business_year }}': business_year,
                 '{{ month }}': month,
                 '{{ zero_month }}': zero_month,
                 '{{ day }}': day,
                 '{{ zero_day }}': zero_day,
                 '{{ org_name }}': org_name}
    
    def __unicode__(self):
        return self.title
    
    def __str__(self):
        return self.title
