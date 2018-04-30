from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import loader
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from .models import Quote


def get_random_quote_or_none():
    try:
        quote = Quote.objects.order_by('?')[0]
    except IndexError:
        quote = None
    return quote


def index(request):

    template = loader.get_template('quotes/index.html')
    context = {
        'daily_url': reverse('daily'),
        'random_url': reverse('random')
    }
    return HttpResponse(template.render(context, request))


def random(request):
    home = reverse('index')
    frequency = 'random'
    quote = get_random_quote_or_none()
    template = loader.get_template('quotes/quotes.html')
    context = {
        'quote': quote,
        'frequency': frequency,
        'home': home,
    }
    return HttpResponse(template.render(context, request))


def daily(request):
    home = reverse('index')
    frequency = 'daily'
    try:
        selected_quote = Quote.objects.filter(selected=True)[0]
    except IndexError:
        selected_quote = get_random_quote_or_none()

    template = loader.get_template('quotes/quotes.html')
    context = {
        'quote': selected_quote,
        'frequency': frequency,
        'home': home,
    }
    return HttpResponse(template.render(context, request))


@never_cache
@csrf_protect
@login_required
def profile(request):

    template = loader.get_template('user/profile.html')
    context = {
        'username': request.user,
    }
    return HttpResponse(template.render(context, request))
