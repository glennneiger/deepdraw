# Generated by Django 2.2.3 on 2019-07-19 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20190711_0230'),
    ]

    operations = [
        migrations.AddField(
            model_name='picinfo',
            name='pic_url',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
