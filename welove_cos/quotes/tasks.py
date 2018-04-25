from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from .models import Quote


def email_notification(title="hello", body="some text"):
    email_user = settings.EMAIL_HOST_USER
    email = EmailMessage(title, body, to=[email_user])
    email.send()


@shared_task
def get_random_quote():
    selected_quotes = Quote.objects.filter(selected=True)
    for quote in selected_quotes:
        quote.selected = False
        quote.save()
    random_quote = Quote.objects.order_by('?')[0]
    random_quote.selected = True
    random_quote.save()

    email_notification("New Random Quote", random_quote.quote_text)

    print("{} - Selected".format(random_quote.quote_text))
