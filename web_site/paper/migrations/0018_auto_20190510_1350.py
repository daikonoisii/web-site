# Generated by Django 2.0.13 on 2019-05-10 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0017_auto_20190510_0932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ourconferencepaper',
            name='published_date',
            field=models.DateField(default=None, help_text='発表した会議が開会した日付を入力してください．', verbose_name='公開年月日'),
        ),
        migrations.AlterField(
            model_name='ourjournalpaper',
            name='published_date',
            field=models.DateField(default=None, verbose_name='出版年月日'),
        ),
    ]
