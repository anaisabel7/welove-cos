from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from mock import patch, call, MagicMock
from .context_processors import COMMON_ORIGIN, TYPE_OF_SOURCE
from .models import Quote, Profile
from .tasks import (
    get_random_quote, send_daily_quote_emails, control_popularity
)
from . import tasks
from .tests import QuoteReadyTestCase


class RandomQuoteTest(QuoteReadyTestCase):

    def test_filtered_queryset(self):
        self.create_quote()
        with patch.object(Quote.objects, 'filter') as mock_quotes_filter:
            get_random_quote()
            mock_quotes_filter.assert_called_with(selected=True)

    def test_random_queryset(self):
        self.create_quote()
        with patch.object(Quote.objects, 'order_by') as mock_quotes_order_by:
            get_random_quote()
            mock_quotes_order_by.assert_called_with("?")

    def test_quote_unselected_and_selected(self):
        previously_selected = self.create_quote(
            text="Pre-selected quote",
            selected=True
        )
        previously_not_selected = self.create_quote(
            text="Non-selected quote"
        )

        with patch.object(
            Quote.objects,
            'order_by',
            return_value=[previously_not_selected]
        ) as mock_quotes_order_by:
            get_random_quote()

        currently_selected = Quote.objects.filter(selected=True)[0]
        currently_not_selected = Quote.objects.filter(selected=False)[0]
        self.assertEqual(
            previously_selected.quote_text,
            currently_not_selected.quote_text
        )
        self.assertEqual(
            previously_not_selected.quote_text,
            currently_selected.quote_text
        )


class DailyQuoteEmailsTest(QuoteReadyTestCase):

    def setUp(self):
        self.quote = self.create_quote(text="Selected quote", selected=True)
        self.user = User.objects.create_user(
            "subscribedpal",
            "subscribedpal@email.com"
        )
        Profile.objects.create(
            user=self.user,
            subscribed=True
        )
        self.title = "Your daily quote from {}".format(COMMON_ORIGIN)
        self.body = "Today's quote from {} is:\n\n\"{}\"\n\nfrom the {} {}.".format(
            COMMON_ORIGIN,
            self.quote.quote_text,
            TYPE_OF_SOURCE,
            self.quote.source
        )
        self.full_url = "https://{}{}".format(
            settings.SITE_DOMAIN, reverse('profile')
        )
        self.closing_msg = "\n\nVisit {} to change your email preferences.".format(
            self.full_url
        )
        self.body = self.body + self.closing_msg

    @patch.object(tasks, 'EmailMessage')
    def test_general_email_content(self, mock_email_message):
        send_daily_quote_emails()
        mock_email_message.assert_called_with(
            self.title,
            self.body,
            to=[self.user.email]
        )

    @patch.object(tasks.EmailMessage, 'send')
    def test_email_sent(self, mock_email_send):
        send_daily_quote_emails()
        mock_email_send.assert_called_once()

    @patch.object(tasks, 'EmailMessage')
    def test_only_selected_quote_sent(self, mock_email_message):
        self.quote.selected = False
        self.quote.save()
        new_quote = self.create_quote(
            text="Another quote that we selected",
            selected=True
        )
        all_quotes = Quote.objects.all()
        self.assertEqual(len(all_quotes), 2)
        self.assertEqual(all_quotes[0], self.quote)

        new_body = "Today's quote from {} is:\n\n\"{}\"\n\nfrom the {} {}.".format(
            COMMON_ORIGIN,
            new_quote.quote_text,
            TYPE_OF_SOURCE,
            new_quote.source
        )
        new_body = new_body + self.closing_msg

        send_daily_quote_emails()
        original_call = call(
            self.title, self.body, to=[self.user.email]
        )
        new_call = call(
            self.title, new_body, to=[self.user.email]
        )
        mock_calls = mock_email_message.mock_calls
        self.assertFalse(original_call in mock_calls)
        self.assertTrue(new_call in mock_calls)

    @patch.object(tasks, 'EmailMessage')
    def test_email_sent_to_subscribed_user_only(self, mock_email_message):
        uninterested_user = User.objects.create_user(
            "uninterestedpal",
            "uninterestedpal@email.com"
        )
        Profile.objects.create(
            user=uninterested_user
        )

        send_daily_quote_emails()
        self.assertEqual(mock_email_message.call_count, 1)
        original_call = call(
            self.title, self.body, to=[self.user.email]
        )
        uninterested_call = call(
            self.title, self.body, to=[uninterested_user.email]
        )
        all_calls = mock_email_message.mock_calls
        self.assertTrue(original_call in all_calls)
        self.assertFalse(uninterested_call in all_calls)


class ControlPopularityTest(QuoteReadyTestCase):

    @patch.object(Quote.objects, 'order_by', return_value=['a'])
    def test_quotes_ordered_by_popularity(self, mock_quotes_order):
        quote = self.create_quote()

        class FakeOrderBy(object):
            reverse = MagicMock(return_value=[quote])

        def side_effect_of_mock(*args, **kwargs):
            return FakeOrderBy

        mock_quotes_order.side_effect = side_effect_of_mock
        control_popularity()
        mock_quotes_order.assert_called_with('popularity')
        mock_quotes_order().reverse.assert_called()

    @patch.object(tasks, 'warning_email_admin')
    def test_popularities_halved_if_popularity_too_high(
        self, mock_warning_email
    ):
        quote = self.create_quote()
        quote.popularity = 5
        quote.save()
        control_popularity()
        mock_warning_email.assert_not_called()
        self.assertEqual(Quote.objects.all()[0].popularity, quote.popularity)

        quote.popularity = 2000000000
        quote.save()
        control_popularity()
        mock_warning_email.assert_called_with(
            "WARNING: All quote popularities are now being divided by half"
        )
        self.assertEqual(Quote.objects.all()[0].popularity, quote.popularity/2)
