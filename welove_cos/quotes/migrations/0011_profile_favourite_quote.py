# Generated by Django 2.0.4 on 2018-05-22 11:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0010_auto_20180517_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='favourite_quote',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quotes.Quote'),
        ),
    ]