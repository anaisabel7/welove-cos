from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template import loader
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from .models import Quote, Profile
from .forms import UserForm, ProfileForm, PollForm


def add_loggedin_user_to_context(request, context):
    current_user = request.user
    if current_user.is_authenticated:
        if current_user.first_name:
            context['loggedin_user'] = current_user.first_name
        else:
            context['loggedin_user'] = current_user.username


def get_random_quote_or_none():
    try:
        quote = Quote.objects.order_by('?')[0]
    except IndexError:
        quote = None
    return quote


def index(request):

    template = loader.get_template('quotes/index.html')
    context = {}
    add_loggedin_user_to_context(request, context)
    return HttpResponse(template.render(context, request))


def random(request):
    frequency = 'random'
    quote = get_random_quote_or_none()
    template = loader.get_template('quotes/quotes.html')
    context = {
        'quote': quote,
        'frequency': frequency,
    }
    add_loggedin_user_to_context(request, context)
    return HttpResponse(template.render(context, request))


def daily(request):
    frequency = 'daily'
    try:
        selected_quote = Quote.objects.filter(selected=True)[0]
    except IndexError:
        selected_quote = get_random_quote_or_none()

    template = loader.get_template('quotes/quotes.html')
    context = {
        'quote': selected_quote,
        'frequency': frequency,
    }
    add_loggedin_user_to_context(request, context)
    return HttpResponse(template.render(context, request))


@login_required
def poll(request):
    template = loader.get_template('polls/poll.html')

    def get_new_choices():
        list_of_choices = []
        no_of_quote_choices = 4
        if Quote.objects.count() < no_of_quote_choices:
            return PollForm.declared_fields['quote_choice'].choices
        for i in range(no_of_quote_choices):
            quote = get_random_quote_or_none()
            while (list_of_choices and
                    quote.quote_text in [x[1] for x in list_of_choices]):
                quote = get_random_quote_or_none()
            list_of_choices.append((quote.id, quote.quote_text))
        return list_of_choices

    context = {}

    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            quote_id = form.cleaned_data['quote_choice']
            chosen_quote = Quote.objects.filter(id=quote_id)[0]
            chosen_quote.popularity = chosen_quote.popularity + 1
            chosen_quote.save()
        else:
            context['errors'] = True
        context['done'] = True

    PollForm.declared_fields['quote_choice'].choices = get_new_choices()
    form = PollForm()
    context['form'] = form
    return HttpResponse(template.render(context, request))


@sensitive_post_parameters()
@never_cache
@csrf_protect
@login_required
def profile(request):
    template = loader.get_template('user/profile.html')
    current_user = request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        users_profile = Profile.objects.filter(user=current_user)[0]
        context = {
            'profile': users_profile,
            'form': form,
        }

        if form.is_valid():
            users_profile.subscribed = form.cleaned_data['subscribed']
            current_user.first_name = form.cleaned_data['first_name']
            users_profile.save()
            current_user.save()
            context['changed'] = True

    else:
        try:
            users_profile = Profile.objects.filter(user=current_user)[0]
        except IndexError:
            users_profile = Profile.objects.create(user=current_user)

        populated_values = {
            'first_name': current_user.first_name,
            'subscribed': users_profile.subscribed,
        }

        form = ProfileForm(populated_values)

        context = {
            'profile': users_profile,
            'form': form,
        }

    return HttpResponse(template.render(context, request))


def send_new_user_email(username, user_email):
    title = "Welcome, {}!".format(username)
    welcome = "Welcome to {}{}!\nWe are glad to have you onboard.\n".format(
        "https://", settings.SITE_DOMAIN
    )
    error = "If you did not just create a user with us, please {}".format(
        "let us know at {} so we can remove your email {}".format(
            settings.EMAIL_HOST_USER, "from our database."
        )
    )
    body = "{}{}".format(welcome, error)
    email_to_send = EmailMessage(title, body, to=[user_email])
    email_to_send.send()


@sensitive_post_parameters()
@never_cache
@csrf_protect
def new_user(request):

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            logout(request)
            new_user = User.objects.create_user(
                form.cleaned_data['username'],
                form.cleaned_data['email']
            )
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            send_new_user_email(
                form.cleaned_data['username'],
                form.cleaned_data['email']
            )
            login(request, new_user)
            return HttpResponseRedirect('profile')
    else:
        form = UserForm()

    return render(request, 'user/new_user.html', {'form': form})
