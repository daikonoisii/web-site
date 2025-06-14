# Generated by Django 2.0.13 on 2019-09-24 22:33

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import picture.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(blank=True, help_text='簡単な説明を入力してください．', max_length=300, null=True, verbose_name='キャプション')),
                ('file', models.ImageField(help_text='写真のファイルを登録してください．', upload_to=picture.models.get_upload_to, validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'], message='JPEG，PNG，またはGIFファイルを添付してださい．')], verbose_name='添付ファイル')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='登録日')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_picture', to=settings.AUTH_USER_MODEL, verbose_name='登録ユーザ')),
            ],
        ),
    ]
