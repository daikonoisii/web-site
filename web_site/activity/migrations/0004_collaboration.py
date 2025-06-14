# Generated by Django 2.0.13 on 2019-11-14 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0003_auto_20191112_2332'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collaboration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fund_name', models.CharField(max_length=100, verbose_name='共同研究先')),
                ('title', models.CharField(max_length=100, verbose_name='タイトル')),
                ('start_date', models.DateField(verbose_name='開始年月日')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='終了年月日')),
            ],
        ),
    ]
