# Generated by Django 2.0.13 on 2019-05-04 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0003_auto_20190504_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='abstract',
            field=models.TextField(null=True, verbose_name='概要'),
        ),
    ]
