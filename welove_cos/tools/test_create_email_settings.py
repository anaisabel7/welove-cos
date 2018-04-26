import argparse
import builtins
import create_email_settings as creator
from mock import patch, mock_open, call, MagicMock
import os
from unittest import TestCase


class CreateEmailSettingsTest(TestCase):

    email = "dummy@gmail.com"
    password = "password"
    file_name = '../welove_cos/email_settings.py'

    def test_find_settings_file(self):
        full_path = creator.find_settings_file()
        script_path = os.path.dirname(creator.__file__)
        if script_path:
            script_path = "{}/".format(script_path)
        settings_path = '{}{}'.format(script_path, self.file_name)
        self.assertEqual(full_path, settings_path)

    @patch("builtins.open")
    def test_opened_file_returned_from_find_settings_file(self, mock_open):
        file_path = "somewhere"

        with patch.object(
            creator, 'find_settings_file', return_value=file_path
        ) as mock_finder:
            creator.create_email_settings(self.email, self.password)

        mock_open.assert_called_with(file_path, 'w+')

    @patch("builtins.open", new_callable=mock_open)
    def test_email_and_password_writen_to_file(self, mock_file):
        creator.create_email_settings(self.email, self.password)
        email_call = call("email = '{}'\n".format(self.email))
        password_call = call("password = '{}'\n".format(self.password))
        mock_file().write.assert_has_calls([
            email_call, password_call
        ])
        mock_file().close.assert_called()

    def test_check_for_gmail_email(self):
        with self.assertRaises(Exception) as context:
            creator.check_for_gmail_email(
                'me@personalemail.com'
            )
        self.assertTrue(
            "A 'gmail' email address is required." in context.exception.args
        )

    @patch.object(creator, 'check_for_gmail_email')
    def test_main_check_for_gmail_email_called(self, mock_gmailchecker):
        class FakeClass(object):
            email = self.email
            password = self.password
        with patch.object(
            argparse, 'ArgumentParser'
        ):
            with patch.object(
                argparse.ArgumentParser(), 'parse_args',
                return_value=FakeClass
            ):
                creator.main()
        mock_gmailchecker.assert_called_with(self.email)

    @patch.object(creator, 'create_email_settings')
    def test_main_create_email_settings_called(self, mock_settingscreator):
        class FakeClass(object):
            email = self.email
            password = self.password
        with patch.object(
            argparse, 'ArgumentParser'
        ):
            with patch.object(
                argparse.ArgumentParser(), 'parse_args',
                return_value=FakeClass
            ):
                with patch.object(creator, 'check_for_gmail_email'):
                    creator.main()
        mock_settingscreator.assert_called_with(
            email=self.email,
            password=self.password
        )
