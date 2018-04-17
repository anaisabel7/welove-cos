from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader

from .models import Quote


def get_random_quote_or_none():
    try:
        quote = Quote.objects.order_by('?')[0]
    except IndexError:
        quote = None
    return quote


def random(request):
    frequency = 'random'
    quote = get_random_quote_or_none()
    template = loader.get_template('quotes/index.html')
    context = {
        'quote': quote,
        'frequency': frequency,
    }
    return HttpResponse(template.render(context, request))


def daily(request):
    frequency = 'daily'
    try:
        selected_quote = Quote.objects.filter(selected=True)[0]
    except IndexError:
        selected_quote = get_random_quote_or_none()

    template = loader.get_template('quotes/index.html')
    context = {
        'quote': selected_quote,
        'frequency': frequency,
    }
    return HttpResponse(template.render(context, request))
