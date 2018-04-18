import copy
from django.conf import settings
from django.urls import reverse
from mock import patch
from .models import Quote
from .tests import QuoteReadyTestCase
from .views import random, daily
from . import context_processors


class RandomViewTest(QuoteReadyTestCase):

    def test_default_message_no_quote(self):
        response = self.client.get(reverse('random'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There is no random quote available")

    def test_random_queryset(self):
        self.create_quote()
        with patch.object(Quote.objects, 'order_by') as mock_quotes_order_by:
            response = self.client.get(reverse('random'))
            mock_quotes_order_by.assert_called_with("?")

    def test_quote_text_and_source_in_response(self):
        self.create_quote()
        response = self.client.get(reverse('random'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.quote_text)
        self.assertContains(response, self.source)


class ViewContextProcessorTest(QuoteReadyTestCase):

    def test_quotes_context_processor(self):
        self.create_quote()
        context = context_processors.quotes_processor(self)
        response = self.client.get(reverse('random'))
        self.assertContains(
            response,
            context['quotes_context']['common_origin']
        )
        self.assertContains(
            response,
            context['quotes_context']['type_of_source']
        )

    def test_no_quotes_context_processor(self):
        self.create_quote()

        templates = copy.deepcopy(settings.TEMPLATES)
        for processor in templates[0]['OPTIONS']['context_processors']:
            if 'quotes_processor' in processor:
                templates[0]['OPTIONS']['context_processors'].remove(processor)

        with self.settings(TEMPLATES=templates):
            context = context_processors.quotes_processor(self)
            response = self.client.get(reverse('random'))
            self.assertNotIn(
                context['quotes_context']['common_origin'],
                str(response.content)
            )
            self.assertNotIn(
                context['quotes_context']['type_of_source'],
                str(response.content)
            )


class DailyViewTest(QuoteReadyTestCase):

    def test_default_message_no_quote(self):
        response = self.client.get(reverse('daily'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There is no daily quote available")

    def test_random_if_no_selected_quote(self):
        self.create_quote()
        with patch.object(Quote.objects, 'order_by') as mock_quotes_order_by:
            response = self.client.get(reverse('daily'))
            mock_quotes_order_by.assert_called_with("?")

    def test_displays_only_selected_quote(self):
        self.create_quote()

        text = "Selected quote text"
        source = "selected quote source"
        selected = True
        self.create_quote(text, source, selected)

        response = self.client.get(reverse('daily'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, text)
        self.assertContains(response, source)
        self.assertNotIn(self.quote_text, str(response.content))

    def test_index_returns_daily_view(self):
        self.create_quote(selected=True)
        response_index = self.client.get(reverse('index'))
        response_daily = self.client.get(reverse('daily'))
        self.assertEqual(response_index.content, response_daily.content)