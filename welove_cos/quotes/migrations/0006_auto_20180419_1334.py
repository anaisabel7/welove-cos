# Generated by Django 2.0.4 on 2018-04-19 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0005_remove_quote_source'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quote',
            old_name='source_model',
            new_name='source',
        ),
    ]
