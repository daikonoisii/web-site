# Generated by Django 2.0.13 on 2019-05-12 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0019_auto_20190510_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conferencepaper',
            name='presentation_id',
            field=models.CharField(blank=True, help_text='研究会，および総合大会，ソサイエティ大会，信越支部大会等の場合は発表IDを入力してください(例1: NS2017-198，例2: IN2018-131，例3: B-7-23，例4: 3D-1)．', max_length=20, null=True, verbose_name='発表ID'),
        ),
        migrations.AlterField(
            model_name='conferencetitle',
            name='country',
            field=models.CharField(blank=True, help_text='開催国(米国，カナダ等の場合は州の略号と開催国)を入力してください(例1: Japan，例2: FL, USA，例3: China)．', max_length=100, verbose_name='開催国'),
        ),
        migrations.AlterField(
            model_name='reference',
            name='title',
            field=models.CharField(help_text='論文のタイトルを入力してください．', max_length=300, verbose_name='タイトル'),
        ),
    ]
