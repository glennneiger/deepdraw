# Generated by Django 2.2.3 on 2019-07-22 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_picinfo_pic_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='picinfo',
            old_name='pic_url',
            new_name='org_pic_url',
        ),
        migrations.AddField(
            model_name='picinfo',
            name='result_pic_url',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]