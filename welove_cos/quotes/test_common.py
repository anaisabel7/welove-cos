import builtins
from django.conf import settings
from django.test import TestCase
from mock import patch
from . import common


class WarningEmailAdminTest(TestCase):

    @patch.object(builtins, 'print')
    def test_message_printed_to_std(self, mock_print):
        common.warning_email_admin(
            warning_text="Hey! You should take a look here!"
        )
        mock_print.assert_called_with("Hey! You should take a look here!")

    @patch.object(common, 'EmailMessage')
    def test_email_sent_correctly(self, mock_email):
        title = "New Warning in {}".format(settings.SITE_DOMAIN)
        intro = "A new warning was detected in {}.\n".format(
            settings.SITE_DOMAIN
        )
        middle = "This is its content:\n\"Hey! You should take a look here\"\n"
        ending = "Warnings often do not need you to take extra actions."
        body = "{}{}{}".format(
            intro, middle, ending
        )

        common.warning_email_admin(
            warning_text="Hey! You should take a look here"
        )
        mock_email.assert_called_with(
            title, body, to=[settings.EMAIL_HOST_USER]
        )
        mock_email().send.assert_called()
