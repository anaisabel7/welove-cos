from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

from .models import Quote


def index(request):
    random_quote = Quote.objects.order_by('?')[0]
    output = "A random quote from City Of Sound is \"%s\"" % random_quote.quote_text
    return HttpResponse(output)
