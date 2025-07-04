# Generated by Django 2.0.13 on 2019-06-08 17:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('output', '0002_auto_20190604_2236'),
    ]

    operations = [
        migrations.AddField(
            model_name='format',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日'),
        ),
        migrations.AlterField(
            model_name='format',
            name='category',
            field=models.IntegerField(choices=[(11, '研究室内 論文誌論文'), (12, '研究室内 会議発表'), (21, '受賞')], default=None, help_text='出力対象のデータの種類を入力してください．', verbose_name='出力データ'),
        ),
    ]
