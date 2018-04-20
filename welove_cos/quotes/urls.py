from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('daily', views.daily, name='daily'),
    path('random', views.random, name='random'),
]
