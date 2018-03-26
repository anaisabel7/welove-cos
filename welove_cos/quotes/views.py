from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader

from .models import Quote


def index(request):
    random_quote = Quote.objects.order_by('?')[0]
    template = loader.get_template('quotes/index.html')
    context = {
        'quote_of_the_day': random_quote,
    }
    return HttpResponse(template.render(context, request))
