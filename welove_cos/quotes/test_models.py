from django.db import models
from mock import patch
from .models import Quote, Source
from .tests import QuoteReadyTestCase


class QuoteTest(QuoteReadyTestCase):
    def test_quote_fields(self):
        fields = {
            'quote_text': models.CharField,
            'source': models.ForeignKey,
            'selected': models.BooleanField
        }
        for name in fields:
            self.assertTrue(hasattr(Quote, name))
            field = Quote._meta.get_field(name)
            self.assertTrue(isinstance(field, fields[name]))

        field_count_plus_id_autofield = len(Quote._meta.get_fields())
        self.assertEqual(field_count_plus_id_autofield, len(fields)+1)

        selected_default = Quote._meta.get_field('selected')._get_default()
        self.assertEqual(selected_default, False)

        source_related_model = Quote._meta.get_field('source').related_model
        self.assertEqual(source_related_model, Source)

        quote_text_max_length = Quote._meta.get_field('quote_text').max_length
        self.assertEqual(quote_text_max_length, 600)

    def test_str_method(self):
        quote = self.create_quote()
        quote_str = quote.__str__()
        self.assertEqual(
            quote_str,
            "A quote from {}".format(quote.source.name)
        )
