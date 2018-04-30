from django.contrib.auth import views as auth_views
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('daily', views.daily, name='daily'),
    path('random', views.random, name='random'),
]

# User / Auth

urlpatterns = urlpatterns + [
    path(
        'login',
        auth_views.LoginView.as_view(
            template_name='user/login.html'
        ),
        name='login'),
    path(
        'logout',
        auth_views.LogoutView.as_view(template_name='user/logout.html'),
        name='logout'
    ),
    path(
        'password_change',
        auth_views.PasswordChangeView.as_view(
            template_name='user/password_change.html'
        ),
        name='password_change'
    ),
    path(
        'password_change_done',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='user/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path('profile', views.profile, name='profile'),
]
