# Generated by Django 2.0.4 on 2018-04-19 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0006_auto_20180419_1334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='link',
            field=models.URLField(max_length=300),
        ),
    ]
