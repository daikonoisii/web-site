# Generated by Django 2.0.13 on 2019-06-08 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('output', '0005_auto_20190608_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='format',
            name='category',
            field=models.CharField(choices=[('our_journal', '研究室内 論文誌論文'), ('our_conference', '研究室内 会議発表'), ('award', '受賞')], default=None, help_text='出力対象のデータの種類を入力してください．', max_length=20, verbose_name='出力データ'),
        ),
    ]
