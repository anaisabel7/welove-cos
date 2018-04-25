from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf.settings import EMAIL_HOST_USER as email_user
from django.core.mail import EmailMessage
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

    email = EmailMessage("New Quote", random_quote.quote_text, to=[email_user])
    email.send()

    print("{} - Selected".format(random_quote.quote_text))
