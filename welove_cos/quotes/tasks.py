from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from .models import Quote, Profile


def email_notification(title="hello", body="some text"):
    subscribed_profiles = Profile.objects.filter(subscribed=True)
    for profile in subscribed_profiles:
        user_email = profile.user.email
        email_to_send = EmailMessage(title, body, to=[user_email])
        email_to_send.send()


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
