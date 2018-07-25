from rest_framework import generics
from quotes.models import Quote
from api.serializers import QuoteSerializer


class DailyApiView(generics.ListAPIView):

    queryset = Quote.objects.filter(selected=True)
    serializer_class = QuoteSerializer
