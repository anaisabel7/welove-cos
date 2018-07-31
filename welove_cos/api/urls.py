from django.urls import path
from api.views import DailyApiView, SingleQuoteApiView, AllQuotesApiView

urlpatterns = [
    path('daily', DailyApiView.as_view(), name='daily_api'),
    path(
        'quote/<int:pk>',
        SingleQuoteApiView.as_view(),
        name='single_quote_api'
    ),
    path('all_quotes', AllQuotesApiView.as_view(), name='all_quotes_api')
]
