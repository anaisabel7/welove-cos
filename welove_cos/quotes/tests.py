from django.test import TestCase
from .models import Quote

# Create your tests here.


class QuoteReadyTestCase(TestCase):

    quote_text = "This band rocks"
    source = "Me"
    selected = False

    def create_quote(self, text=quote_text, source=source, selected=selected):
        quote_object = Quote.objects.create(
            quote_text=text,
            source=source,
            selected=selected
        )
        return quote_object
