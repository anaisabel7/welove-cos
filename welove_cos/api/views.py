from rest_framework import generics
from quotes.models import Quote
from api.serializers import QuoteSerializer


class DailyApiView(generics.ListAPIView):

    queryset = Quote.objects.filter(selected=True)
    serializer_class = QuoteSerializer


class AllQuotesApiView(generics.ListAPIView):

    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer


class SingleQuoteApiView(generics.RetrieveAPIView):

    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
