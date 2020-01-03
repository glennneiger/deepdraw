# Generated by Django 2.2.3 on 2019-08-08 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20190722_0433'),
    ]

    operations = [
        migrations.AddField(
            model_name='picinfo',
            name='pic_bg',
            field=models.CharField(default=1, max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='picinfo',
            name='pic_org_size',
            field=models.CharField(default=1, max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='picinfo',
            name='pic_size',
            field=models.CharField(default=1, max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskinfo',
            name='bg',
            field=models.CharField(default=1, max_length=3200000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskinfo',
            name='org_size',
            field=models.CharField(default=1, max_length=3200000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskinfo',
            name='size',
            field=models.CharField(default=1, max_length=3200000),
            preserve_default=False,
        ),
    ]