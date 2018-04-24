import builtins
import create_email_settings as creator
from mock import patch, mock_open, call
from unittest import TestCase


class CreateEmailSettingsTest(TestCase):

    email = "dummy@gmail.com"
    password = "password"
    file_name = '../welove_cos/email_settings.py'

    @patch("builtins.open")
    def test_correct_file_opened(self, mock_open):
        creator.create_email_settings(self.email, self.password)
        mock_open.assert_called_with(self.file_name, 'w+')

    @patch("builtins.open", new_callable=mock_open)
    def test_email_and_password_writen_to_file(self, mock_file):
        creator.create_email_settings(self.email, self.password)
        email_call = call("email = {}".format(self.email))
        password_call = call("password = {}".format(self.password))
        mock_file().write.assert_has_calls([
            email_call, password_call
        ])
        mock_file().close.assert_called()

    @patch("builtins.open")
    def test_exception_raised_for_not_gmail_emails(self, mock_open):
        with self.assertRaises(Exception) as context:
            creator.create_email_settings(
                'me@personalemail.com', self.password
            )
        self.assertTrue(
            "A 'gmail' email address is required." in context.exception.args
        )
