from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Quote


@shared_task
def get_random_quote():
    selected_quotes = Quote.objects.filter(selected=True)
    for quote in selected_quotes:
        quote.selected = False
        quote.save()
    random_quote = Quote.objects.order_by('?')[0]
    random_quote.selected = True
    random_quote.save()

    print("{} - Selected".format(random_quote.quote_text))
