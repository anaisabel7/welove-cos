# Generated by Django 2.0.4 on 2018-04-19 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0004_transfer_source'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quote',
            name='source',
        ),
    ]
