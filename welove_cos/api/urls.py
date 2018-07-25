from django.urls import path
from api.views import DailyApiView

urlpatterns = [
    path('daily', DailyApiView.as_view(), name='daily_api')
]
