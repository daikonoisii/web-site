# Generated by Django 2.0.13 on 2019-11-07 22:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0011_information'),
    ]

    operations = [
        migrations.RenameField(
            model_name='information',
            old_name='conference_title',
            new_name='picture',
        ),
    ]
