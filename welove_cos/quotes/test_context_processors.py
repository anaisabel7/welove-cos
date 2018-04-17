from django.test import TestCase
import mock
from .context_processors import quotes_processor

COMMON_ORIGIN = "City Of Sound"
TYPE_OF_SOURCE = "song"

CONTEXT_DICT = {
    'quotes_context': {
        'common_origin': COMMON_ORIGIN,
        'type_of_source': TYPE_OF_SOURCE
    }
}


class ContextProcessorsTest(TestCase):
    def test_context_values(self):
        request = mock.Mock()
        context = quotes_processor(request)
        self.assertEqual(context, CONTEXT_DICT)
