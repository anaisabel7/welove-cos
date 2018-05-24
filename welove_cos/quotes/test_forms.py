from django import forms
from django.contrib.auth.models import User
from django.test import TestCase
from .forms import UserForm, ProfileForm, PollForm, FavouriteQuoteForm
from .models import Profile


class UserFormTest(TestCase):

    def test_model_of_ModelForm(self):
        self.assertEqual(
            UserForm._meta.model,
            User
        )

    def test_fields(self):
        expected_fields = ['username', 'email', 'password']
        actual_fields = UserForm._meta.fields

        # Being a list, the order matters
        for each in expected_fields:
            self.assertIn(each, actual_fields)

        self.assertEqual(len(expected_fields), len(actual_fields))

    def test_help_texts(self):
        expected_help_texts = {
            'username': None,
        }
        actual_help_texts = UserForm._meta.help_texts

        self.assertEqual(expected_help_texts, actual_help_texts)

    def test_widgets(self):
        expected_widgets = {
            'password': forms.PasswordInput,
        }

        self.assertEqual(len(expected_widgets), len(UserForm._meta.widgets))
        actual_widgets = UserForm._meta.widgets
        for each_key in expected_widgets:
            self.assertIn(each_key, actual_widgets)
            self.assertTrue(isinstance(
                UserForm._meta.widgets[each_key],
                expected_widgets[each_key]
            ))


class ProfileFormTest(TestCase):

    def test_model_of_ModelForm(self):
        self.assertEqual(
            ProfileForm._meta.model,
            Profile
        )

    def test_fields(self):
        expected_meta_fields = ['subscribed']
        actual_meta_fields = ProfileForm._meta.fields
        for each in expected_meta_fields:
            self.assertIn(each, actual_meta_fields)

        expected_extra_fields = {
            'first_name': forms.CharField
        }

        actual_fields = ProfileForm.base_fields
        for each_key in expected_extra_fields:
            self.assertIn(each_key, actual_fields)
            self.assertTrue(isinstance(
                actual_fields[each_key],
                expected_extra_fields[each_key]
            ))

    def test_first_name(self):
        self.assertEqual(
            ProfileForm.base_fields['first_name'].label,
            'First name'
        )
        self.assertEqual(
            ProfileForm.base_fields['first_name'].required,
            False
        )
        self.assertEqual(
            ProfileForm.base_fields['first_name'].max_length,
            User._meta.get_field('first_name').max_length
        )

    def test_meta_labels(self):
        expected_labels = {
            'subscribed': 'Subscribed to daily quote emails',
        }
        self.assertEqual(
            expected_labels,
            ProfileForm._meta.labels
        )

    def test_field_order(self):
        expected_order = ['first_name', 'subscribed']
        self.assertEqual(
            expected_order,
            ProfileForm.field_order
        )


class PollFormTest(TestCase):
    def test_fields(self):
        expected_fields = {
            'quote_choice': forms.ChoiceField,
        }
        actual_fields = PollForm.base_fields
        for each_key in expected_fields:
            self.assertIn(each_key, actual_fields)
            self.assertTrue(isinstance(
                actual_fields[each_key],
                expected_fields[each_key]
            ))

    def test_quote_choice_parameters(self):
        expected_choices = [
            (1, 'There is a problem with the poll,'),
            (2, 'there are no available quotes.'),
            (3, 'There is nothing to see here.'),
            (4, 'We are sorry :( ')
        ]
        actual_choices = PollForm.declared_fields['quote_choice'].choices
        self.assertEqual(expected_choices, actual_choices)

        expected_required = True
        actual_required = PollForm.declared_fields['quote_choice'].required
        self.assertEqual(expected_required, actual_required)

        expected_widget_class = forms.RadioSelect
        actial_widget = PollForm.declared_fields['quote_choice']. widget
        self.assertTrue(isinstance(actial_widget, expected_widget_class))

        expected_label = 'Choose the quote you like the most'
        actual_label = PollForm.declared_fields['quote_choice'].label
        self.assertEqual(expected_label, actual_label)


class FavouriteQuoteFormTest(TestCase):
    def test_fields(self):
        expected_fields = {
            'set_favourite': forms.BooleanField,
        }
        actual_fields = FavouriteQuoteForm.base_fields
        for each_key in expected_fields:
            self.assertIn(each_key, actual_fields)
            self.assertTrue(isinstance(
                actual_fields[each_key],
                expected_fields[each_key]
            ))

    def test_set_favourite_parameters(self):
        set_favourite_initial = FavouriteQuoteForm.declared_fields[
            'set_favourite'].initial
        self.assertEqual(set_favourite_initial, False)
        set_favourite_required = FavouriteQuoteForm.declared_fields[
            'set_favourite'].required
        self.assertEqual(set_favourite_required, False)
        set_favourite_label = FavouriteQuoteForm.declared_fields[
            'set_favourite'].label
        self.assertEqual(set_favourite_label, '')
        set_favourite_widget = FavouriteQuoteForm.declared_fields[
            'set_favourite'].widget
        self.assertTrue(isinstance(set_favourite_widget, forms.CheckboxInput))
        set_fav_widget_attrs = FavouriteQuoteForm.declared_fields[
            'set_favourite'].widget.attrs
        self.assertEqual(
            set_fav_widget_attrs, {'onclick': 'this.form.submit();'}
        )
