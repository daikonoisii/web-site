# Generated by Django 2.0.13 on 2020-07-18 23:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='price',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0, message='価格は正の値でなければなりません．')], verbose_name='価格'),
            preserve_default=False,
        ),
    ]
