# Generated by Django 2.0.13 on 2019-10-06 17:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0004_qanda'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='イベント')),
                ('month', models.IntegerField(help_text='イベントを実施する付きを入力してください(1〜12)．', validators=[django.core.validators.MinValueValidator(1, message='1より小さい値は入力できません．'), django.core.validators.MaxValueValidator(12, message='12より大きい値は入力できません．')], verbose_name='実施月')),
            ],
        ),
    ]
