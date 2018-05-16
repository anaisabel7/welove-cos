from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password'
        ]
        widgets = {
            'password': forms.PasswordInput(),
        }
        help_texts = {
            'username': None,
        }


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=User._meta.get_field('first_name').max_length,
        label='First name',
        required=False
    )

    class Meta:
        model = Profile
        fields = ['subscribed']
        labels = {
            'subscribed': 'Subscribed to daily quote emails'
        }

    field_order = ['first_name', 'subscribed']


class PollForm(forms.Form):
    quote_choice = forms.ChoiceField(
        choices=[
            (1, 'There is a problem with the poll,'),
            (2, 'there are no available quotes.'),
            (3, 'There is nothing to see here.'),
            (4, 'We are sorry :( ')
        ],
        required=True,
        widget=forms.RadioSelect,
        label='Choose the quote you like the most'
    )
