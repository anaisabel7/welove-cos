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
        auth_views.LogoutView.as_view(
            template_name='user/logout.html'
        ),
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
    path(
        'lost_password',
        auth_views.PasswordResetView.as_view(
            email_template_name='user/reset_password_email.html',
            success_url='lost_password_done',
            template_name='user/lost_password.html'
        ),
        name='lost_password'
    ),
    path(
        'lost_password_done',
        auth_views.PasswordResetDoneView.as_view(
            template_name='user/lost_password_done.html'
        ),
        name='lost_password_done'
    ),
    path(
        'reset_password/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            success_url='/reset_password_done',
            template_name='user/reset_password.html'
        ),
        name='reset_password'
    ),
    path(
        'reset_password_done',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user/reset_password_done.html'
        ),
        name='reset_password_done'
    ),
    path('profile', views.profile, name='profile'),
    path('new_user', views.new_user, name='new_user')
]
