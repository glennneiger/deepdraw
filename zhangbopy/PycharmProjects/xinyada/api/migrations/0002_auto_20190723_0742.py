# Generated by Django 2.2.3 on 2019-07-23 07:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserInfo',
            new_name='PicInfo',
        ),
    ]