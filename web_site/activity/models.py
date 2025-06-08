from django.db import models


class ProfessionalActivity(models.Model):
    """委員会など"""
    title = models.CharField('タイトル', max_length=400)
    start_date = models.DateField('開始年月日')
    end_date = models.DateField('終了年月日', null=True, blank=True)
    
    def __unicode__(self):
        return self.title
    
    def __str__(self):
        return self.title
    
    def activity_title(self):
        """タイトル"""
        return self.title
    
    def activity_start_date(self):
        """委員の開始年月"""
        return str(self.start_date.strftime('%Y%m'))

    def activity_end_date(self):
        """委員の終了年月"""
        if self.end_date is None:
            return ''
        return str(self.end_date.strftime('%Y%m'))
    
    def end_date_or_999999(self):
        """委員の終了年月 (情報がなければ999999)"""
        if self.end_date is None:
            return '999999'
        return str(self.end_date.strftime('%Y%m'))
    
    def society_1_or_2(self):
        """学会主催ならば1，そうでなければ2"""
        if any([x in self.title for x in ['学会', 'IEEE', 'IEICE', 'IFIP']]):
            return '1'
        return '2'
    
    def society_1_gov_2_loc_3_or_4(self):
        """学会関係ならば1，政府系ならば2，自治体系ならば3，その他なら4"""
        if any([x in self.title for x in ['学会', 'IEEE', 'IEICE', 'IFIP']]):
            return '1'
        if any([x in self.title for x in ['省', '庁']]):
            return '2'
        if any([x in self.title for x in ['県', '東京都', '大阪府', '京都府', '北海道']]):
            return '3'
        return '4'
    
    # 置き換え文字列と関数の対応
    VARIABLES = {'{{ title }}': activity_title,
                 '{{ start_date }}': activity_start_date,
                 '{{ end_date }}': activity_end_date,
                 '{{ end_date_or_999999 }}': end_date_or_999999,
                 '{{ society_1_or_2 }}': society_1_or_2,
                 '{{ society_1_gov_2_loc_3_or_4 }}': society_1_gov_2_loc_3_or_4,
                 }


class Fund(models.Model):
    """競争的資金など"""
    ROLE = (
        ('principal', '代表'),
        ('co-investigator', '分担'),
    )
    
    CATEGORY = (
        ('kakenhi', '科研費'),
        ('internal', '学内資金'),
        ('others', 'その他'),
    )
    
    role = models.CharField('代表/分担', choices=ROLE, max_length=15)
    category = models.CharField('カテゴリ', choices=CATEGORY, max_length=15)
    fund_name = models.CharField('研究助成名称', max_length=100)
    title = models.CharField('タイトル', max_length=100)
    start_date = models.DateField('開始年月日')
    end_date = models.DateField('終了年月日')
    
    def __unicode__(self):
        return '{} - {}'.format(self.fund_name, self.title)
    
    def __str__(self):
        return '{} - {}'.format(self.fund_name, self.title)


class Collaboration(models.Model):
    """共同研究など"""
    company = models.CharField('共同研究先', max_length=100)
    title = models.CharField('タイトル', max_length=100)
    start_date = models.DateField('開始年月日')
    end_date = models.DateField('終了年月日', null=True, blank=True)
    
    def __unicode__(self):
        return '{} - {}'.format(self.company, self.title)
    
    def __str__(self):
        return '{} - {}'.format(self.company, self.title)
