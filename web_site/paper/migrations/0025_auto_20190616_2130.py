# Generated by Django 2.0.13 on 2019-06-16 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0024_auto_20190616_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conferencetitle',
            name='snip',
            field=models.FloatField(blank=True, help_text='研究室メンバが著者にいる論文でSNIPが記録されている会議の場合は，この年の会議のSNIPを記入してください．', max_length=100, null=True, verbose_name='SNIP'),
        ),
    ]
