from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import loader
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from .models import Quote, Profile
from .forms import UserForm, ProfileForm


def add_loggedin_user_to_context(request, context):
    current_user = request.user
    if current_user.is_authenticated:
        if current_user.first_name:
            context['loggedin_user'] = current_user.first_name
        else:
            context['loggedin_user'] = current_user.username


def get_random_quote_or_none():
    try:
        quote = Quote.objects.order_by('?')[0]
    except IndexError:
        quote = None
    return quote


def index(request):

    template = loader.get_template('quotes/index.html')
    context = {}
    add_loggedin_user_to_context(request, context)
    return HttpResponse(template.render(context, request))


def random(request):
    frequency = 'random'
    quote = get_random_quote_or_none()
    template = loader.get_template('quotes/quotes.html')
    context = {
        'quote': quote,
        'frequency': frequency,
    }
    add_loggedin_user_to_context(request, context)
    return HttpResponse(template.render(context, request))


def daily(request):
    frequency = 'daily'
    try:
        selected_quote = Quote.objects.filter(selected=True)[0]
    except IndexError:
        selected_quote = get_random_quote_or_none()

    template = loader.get_template('quotes/quotes.html')
    context = {
        'quote': selected_quote,
        'frequency': frequency,
    }
    add_loggedin_user_to_context(request, context)
    return HttpResponse(template.render(context, request))


@sensitive_post_parameters()
@never_cache
@csrf_protect
@login_required
def profile(request):
    template = loader.get_template('user/profile.html')
    current_user = request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        users_profile = Profile.objects.filter(user=current_user)[0]
        context = {
            'profile': users_profile,
            'form': form,
        }

        if form.is_valid():
            users_profile.subscribed = form.cleaned_data['subscribed']
            current_user.first_name = form.cleaned_data['first_name']
            users_profile.save()
            current_user.save()
            context['changed'] = True

    else:
        try:
            users_profile = Profile.objects.filter(user=current_user)[0]
        except IndexError:
            users_profile = Profile.objects.create(user=current_user)

        populated_values = {
            'first_name': current_user.first_name,
            'subscribed': users_profile.subscribed,
        }

        form = ProfileForm(populated_values)

        context = {
            'profile': users_profile,
            'form': form,
        }

    return HttpResponse(template.render(context, request))


@sensitive_post_parameters()
@never_cache
@csrf_protect
def new_user(request):

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            logout(request)
            new_user = User.objects.create_user(
                form.cleaned_data['username'],
                form.cleaned_data['email']
            )
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            login(request, new_user)
            return HttpResponseRedirect('profile')
    else:
        form = UserForm()

    return render(request, 'user/new_user.html', {'form': form})
