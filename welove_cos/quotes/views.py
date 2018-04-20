from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
from django.urls import reverse

from .models import Quote


def get_random_quote_or_none():
    try:
        quote = Quote.objects.order_by('?')[0]
    except IndexError:
        quote = None
    return quote


def index(request):
    template = loader.get_template('quotes/index.html')
    context = {}
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
