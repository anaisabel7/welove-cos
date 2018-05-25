from django.test import TestCase
import mock
from .context_processors import quotes_processor, message_processor
from .models import Message

COMMON_ORIGIN = "City Of Sound"
TYPE_OF_SOURCE = "song"

CONTEXT_DICT = {
    'quotes_context': {
        'common_origin': COMMON_ORIGIN,
        'type_of_source': TYPE_OF_SOURCE
    }
}


class QuotesProcessorTest(TestCase):
    def test_context_values(self):
        request = mock.Mock()
        context = quotes_processor(request)
        self.assertEqual(context, CONTEXT_DICT)


class MessageProcessorTest(TestCase):
    def test_message_context_none_if_no_messages(self):
        no_message_context = {
            'message_context': {
                'message': None
            }
        }
        request = mock.Mock()
        self.assertEqual(Message.objects.count(), 0)
        context = message_processor(request)
        self.assertEqual(context, no_message_context)

    def test_message_context_none_if_no_displayed_messages(self):
        no_message_context = {
            'message_context': {
                'message': None
            }
        }
        request = mock.Mock()
        Message.objects.create(message_text="hey", displayed=False)
        self.assertEqual(Message.objects.filter(displayed=True).count(), 0)
        context = message_processor(request)
        self.assertEqual(context, no_message_context)

    def test_message_context_contains_displayed_message(self):
        message_text = "You Need To Know!"
        Message.objects.create(message_text=message_text, displayed=True)
        displayed_message_context = {
            'message_context': {
                'message': message_text
            }
        }
        request = mock.Mock()
        context = message_processor(request)
        self.assertEqual(context, displayed_message_context)
