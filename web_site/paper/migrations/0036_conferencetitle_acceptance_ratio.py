# Generated by Django 2.0.13 on 2019-08-18 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0035_auto_20190817_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='conferencetitle',
            name='acceptance_ratio',
            field=models.FloatField(blank=True, help_text='研究室メンバが著者にいる論文で採択率が公開されている場合は，この年の会議の採択率を記入してください．', max_length=400, null=True, verbose_name='採択率'),
        ),
    ]
