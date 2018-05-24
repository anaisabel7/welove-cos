from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase
from mock import patch
from .models import Quote, Source, Profile
from .tests import QuoteReadyTestCase


class QuoteTest(QuoteReadyTestCase):
    def test_quote_fields(self):
        fields = {
            'quote_text': models.CharField,
            'source': models.ForeignKey,
            'selected': models.BooleanField,
            'popularity': models.IntegerField
        }
        for name in fields:
            self.assertTrue(hasattr(Quote, name))
            field = Quote._meta.get_field(name)
            self.assertTrue(isinstance(field, fields[name]))

        field_count_plus_id_and_rel_profile = len(Quote._meta.get_fields())
        self.assertEqual(field_count_plus_id_and_rel_profile, len(fields)+2)

        selected_default = Quote._meta.get_field('selected')._get_default()
        self.assertEqual(selected_default, False)

        source_related_model = Quote._meta.get_field('source').related_model
        self.assertEqual(source_related_model, Source)

        source_on_delete = Quote._meta.get_field(
            'source'
        ).remote_field.on_delete
        self.assertEqual(source_on_delete, models.CASCADE)

        quote_text_max_length = Quote._meta.get_field('quote_text').max_length
        self.assertEqual(quote_text_max_length, 600)

        quote_text_unique = Quote._meta.get_field('quote_text').unique
        self.assertEqual(quote_text_unique, True)

        popularity_default = Quote._meta.get_field('popularity')._get_default()
        self.assertEqual(selected_default, 0)

    def test_str_method(self):
        quote = self.create_quote()
        quote_str = quote.__str__()
        self.assertEqual(
            quote_str,
            "A quote from {}".format(quote.source.name)
        )


class SourceTest(QuoteReadyTestCase):
    def test_source_fields(self):
        fields = {
            'name': models.CharField,
            'link': models.URLField,
        }
        for each in fields:
            self.assertTrue(hasattr(Source, each))
            field = Source._meta.get_field(each)
            self.assertTrue(isinstance(field, fields[each]))

        field_count_plus_id_and_rel_quote = len(Source._meta.get_fields())
        self.assertEqual(field_count_plus_id_and_rel_quote, len(fields)+2)

        source_name_max_length = Source._meta.get_field('name').max_length
        self.assertEqual(source_name_max_length, 100)

        source_link_max_length = Source._meta.get_field('link').max_length
        self.assertEqual(source_link_max_length, 300)

    def test_str_method(self):
        source = self.create_source()
        source_str = source.__str__()
        self.assertEqual(source_str, source.name)


class ProfileTest(TestCase):
    def test_profile_fields(self):
        fields = {
            'user': models.OneToOneField,
            'subscribed': models.BooleanField,
            'favourite_quote': models.ForeignKey,
        }
        for each in fields:
            self.assertTrue(hasattr(Profile, each))
            field = Profile._meta.get_field(each)
            self.assertTrue(isinstance(field, fields[each]))

        field_count_plus_id_autofield = len(Profile._meta.get_fields())
        self.assertEqual(field_count_plus_id_autofield, len(fields)+1)

        user_related_model = Profile._meta.get_field('user').related_model
        self.assertEqual(user_related_model, User)

        fav_quote_related_model = Profile._meta.get_field(
            'favourite_quote'
        ).related_model
        self.assertEqual(fav_quote_related_model, Quote)

        fav_quote_blank = Profile._meta.get_field('favourite_quote').blank
        self.assertEqual(fav_quote_blank, True)

        fav_quote_null = Profile._meta.get_field('favourite_quote').null
        self.assertEqual(fav_quote_null, True)

        fav_quote_on_delete = Profile._meta.get_field(
            'favourite_quote'
        ).remote_field.on_delete
        self.assertEqual(fav_quote_on_delete, models.SET_NULL)

        subscribed_default = Profile._meta.get_field(
            'subscribed'
        )._get_default()
        self.assertEqual(subscribed_default, False)

    def test_str_method(self):
        user = User.objects.create_user('username', 'email@email.com')
        profile = Profile.objects.create(user=user)
        profile_str = profile.__str__()
        self.assertEqual(profile_str, "The profile of {}".format(user))
