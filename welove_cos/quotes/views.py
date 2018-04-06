from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader

from .models import Quote


def random(request):
    frequency = 'random'
    quote = Quote.objects.order_by('?')[0]
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
        selected_quote = Quote.objects.order_by('?')[0]

    template = loader.get_template('quotes/index.html')
    context = {
        'quote': selected_quote,
        'frequency': frequency,
    }
    return HttpResponse(template.render(context, request))
