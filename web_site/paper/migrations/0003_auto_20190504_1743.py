# Generated by Django 2.0.13 on 2019-05-04 17:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('paper', '0002_reference_citation_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='citation_key',
            field=models.SlugField(default=None, max_length=20, null=True, unique=True, verbose_name='引用コード'),
        ),
        migrations.AlterField(
            model_name='reference',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_papers', to=settings.AUTH_USER_MODEL, verbose_name='登録ユーザ'),
        ),
    ]
