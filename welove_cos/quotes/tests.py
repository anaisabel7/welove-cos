from django.contrib.auth.models import User
from django.test import TestCase
from .models import Quote, Source, Profile

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


class UserReadyTestCase(TestCase):

    username = 'awesomeuser'
    email = 'awesome@email.com'
    password = 'password'

    def create_and_login_user(
        self, username=username, email=email, password=password
    ):
        self.user = User.objects.create_user(username, email, password)
        self.client.login(username=username, password=password)

    def create_user_login_and_profile(
        self,
        username=username, email=email, password=password, subscribed=False
    ):
        self.create_and_login_user(
            username=username, email=email, password=password
        )
        self.profile = Profile.objects.create(
            user=self.user, subscribed=subscribed
        )
