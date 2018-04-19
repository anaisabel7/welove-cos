# Generated by Django 2.0.4 on 2018-04-19 10:40

from django.db import migrations


def transfer_source(apps, schema_editor):
    Quote = apps.get_model('quotes', 'Quote')
    Source = apps.get_model('quotes', 'Source')
    for quote in Quote.objects.all():
        source_of_quote = Source.objects.filter(name=quote.source)
        if len(source_of_quote) == 0:
            source = Source.objects.create(name=quote.source)
        else:
            source = source_of_quote[0]
        quote.source_model = source
        quote.save()


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0003_auto_20180419_1235'),
    ]

    operations = [
        migrations.RunPython(transfer_source),
    ]
