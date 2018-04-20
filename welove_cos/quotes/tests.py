from django.test import TestCase
from .models import Quote, Source

# Create your tests here.


class QuoteReadyTestCase(TestCase):

    quote_text = "This band rocks"
    source_name = "Me"
    selected = False
    link = ''

    def create_source(self, name=source_name, link=link):
        source_object = Source.objects.create(
            name=name,
            link=link,
        )
        return source_object

    def create_quote(self, text=quote_text, source=None, selected=selected):
        if source is None:
            source = self.create_source()
        quote_object = Quote.objects.create(
            quote_text=text,
            source=source,
            selected=selected
        )
        return quote_object
