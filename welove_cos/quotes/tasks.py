from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Quote


@shared_task
def get_random_quote():
    random_quote = Quote.objects.order_by('?')[0]
    return random_quote
