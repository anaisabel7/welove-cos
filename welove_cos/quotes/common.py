from django.conf import settings
from django.core.mail import EmailMessage


def warning_email_admin(warning_text="WARNING: Unknown warning"):
    print(warning_text)

    admin_email = settings.EMAIL_HOST_USER
    title = "New Warning in {}".format(settings.SITE_DOMAIN)
    body_intro = "A new warning was detected in {}.\n".format(
        settings.SITE_DOMAIN
    )
    body_middle = "This is its content:\n\"{}\"\n".format(
        warning_text
    )
    body_ending = "Warnings often do not need you to take extra actions."
    body = "{}{}{}".format(
        body_intro, body_middle, body_ending
    )
    email_to_send = EmailMessage(title, body, to=[admin_email])
    email_to_send.send()
