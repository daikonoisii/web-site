# Generated by Django 2.0.13 on 2019-08-20 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0040_auto_20190820_2233'),
    ]

    operations = [
        migrations.AddField(
            model_name='ourconferencepaper',
            name='fwci',
            field=models.FloatField(blank=True, default=None, help_text='FWCIを表示します．', null=True, verbose_name='FWCI'),
        ),
        migrations.AddField(
            model_name='ourjournalpaper',
            name='fwci',
            field=models.FloatField(blank=True, default=None, help_text='FWCIを表示します．', null=True, verbose_name='FWCI'),
        ),
    ]
