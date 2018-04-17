from django.test import TestCase
from mock import patch
from .models import Quote
from .tasks import get_random_quote
from .test_views import QuoteReadyTestCase


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
