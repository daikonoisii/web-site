# Generated by Django 2.0.13 on 2020-10-02 23:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0006_item_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='kyash_qr',
        ),
        migrations.RemoveField(
            model_name='item',
            name='kyash_url',
        ),
        migrations.RemoveField(
            model_name='item',
            name='paypay_qr',
        ),
        migrations.RemoveField(
            model_name='item',
            name='paypay_url',
        ),
    ]
