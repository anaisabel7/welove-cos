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
