from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.urls import reverse
from .models import Quote, Profile
from .context_processors import COMMON_ORIGIN, TYPE_OF_SOURCE


@shared_task
def send_daily_quote_emails():
    subscribed_profiles = Profile.objects.filter(subscribed=True)
    title = "Your daily quote from {}".format(COMMON_ORIGIN)
    quote = Quote.objects.filter(selected=True)[0]
    body = "Today's quote from {} is:\n\n\"{}\"\n\nfrom the {} {}.".format(
        COMMON_ORIGIN,
        quote.quote_text,
        TYPE_OF_SOURCE,
        quote.source
    )
    site_domain = Site.objects.get_current().domain
    closing_msg = "\n\nVisit {}{} to change your email preferences.".format(
        site_domain, reverse('profile')
    )
    body = body + closing_msg
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

    print("{} - Selected".format(random_quote.quote_text))
