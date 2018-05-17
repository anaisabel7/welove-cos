import copy
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import QueryDict, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.test import TestCase, RequestFactory
from mock import patch, call
from .forms import ProfileForm
from .models import Quote, Profile
from .tests import QuoteReadyTestCase, UserReadyTestCase
from . import context_processors
from . import views


class RandomViewTest(QuoteReadyTestCase):

    def test_default_message_no_quote(self):
        response = self.client.get(reverse('random'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There is no random quote available")

    def test_random_queryset(self):
        self.create_quote()
        with patch.object(Quote.objects, 'order_by') as mock_quotes_order_by:
            response = self.client.get(reverse('random'))
            mock_quotes_order_by.assert_called_with("?")

    def test_quote_text_and_source_in_response(self):
        self.create_quote()
        response = self.client.get(reverse('random'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.quote_text)
        self.assertContains(response, self.source_name)


class ViewContextProcessorTest(QuoteReadyTestCase):

    def test_quotes_context_processor(self):
        self.create_quote()
        context = context_processors.quotes_processor(self)
        response = self.client.get(reverse('random'))
        self.assertContains(
            response,
            context['quotes_context']['common_origin']
        )
        self.assertContains(
            response,
            context['quotes_context']['type_of_source']
        )

    def test_no_quotes_context_processor(self):
        self.create_quote()

        templates = copy.deepcopy(settings.TEMPLATES)
        for processor in templates[0]['OPTIONS']['context_processors']:
            if 'quotes_processor' in processor:
                templates[0]['OPTIONS']['context_processors'].remove(processor)

        with self.settings(TEMPLATES=templates):
            context = context_processors.quotes_processor(self)
            response = self.client.get(reverse('random'))
            self.assertNotIn(
                context['quotes_context']['common_origin'],
                str(response.content)
            )
            self.assertNotIn(
                context['quotes_context']['type_of_source'],
                str(response.content)
            )


class DailyViewTest(QuoteReadyTestCase):

    def test_default_message_no_quote(self):
        response = self.client.get(reverse('daily'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There is no daily quote available")

    def test_random_if_no_selected_quote(self):
        self.create_quote()
        with patch.object(Quote.objects, 'order_by') as mock_quotes_order_by:
            response = self.client.get(reverse('daily'))
            mock_quotes_order_by.assert_called_with("?")

    def test_displays_only_selected_quote(self):
        self.create_quote()

        text = "Selected quote text"
        source_name = "selected quote source"
        selected = True
        source = self.create_source(name=source_name)
        self.create_quote(text, source, selected)

        response = self.client.get(reverse('daily'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, text)
        self.assertContains(response, source_name.title())
        self.assertNotIn(self.quote_text, str(response.content))

    def test_index_does_not_return_daily_view(self):
        self.create_quote(selected=True)
        response_index = self.client.get(reverse('index'))
        response_daily = self.client.get(reverse('daily'))
        self.assertNotEqual(response_index.content, response_daily.content)


class IndexViewTest(TestCase):

    def test_random_and_daily_urls_in_index(self):
        response = self.client.get(reverse('index'))
        daily_url = reverse('daily')
        random_url = reverse('random')
        self.assertContains(response, daily_url)
        self.assertContains(response, random_url)

    def test_no_context_processor_index(self):
        templates = copy.deepcopy(settings.TEMPLATES)
        for processor in templates[0]['OPTIONS']['context_processors']:
            if 'quotes_processor' in processor:
                templates[0]['OPTIONS']['context_processors'].remove(processor)

        with self.settings(TEMPLATES=templates):
            context = context_processors.quotes_processor(self)
            response = self.client.get(reverse('index'))
            self.assertContains(response, "Quotes")
            self.assertNotIn(
                context['quotes_context']['common_origin'],
                str(response.content)
            )

    def test_context_processor_index(self):
        context = context_processors.quotes_processor(self)
        response = self.client.get(reverse('index'))
        self.assertContains(
            response,
            context['quotes_context']['common_origin']
        )


class PollViewTest(UserReadyTestCase, QuoteReadyTestCase):
    def test_bottom_link_displayed_correctly(self):
        self.create_and_login_user()
        response = self.client.get(reverse('poll'))
        self.assertContains(
            response, "Would you like to go back to your profile?"
        )
        self.assertContains(response, reverse('profile'))

    def test_submit_button_displayed(self):
        self.create_and_login_user()
        response = self.client.get(reverse('poll'))
        self.assertContains(response, '<input type="submit" value="Submit" />')

    def test_default_quotes_if_less_than_4_quotes_available(self):
        self.create_and_login_user()
        self.create_quote()
        response = self.client.get(reverse('poll'))
        self.assertContains(response, "no available quotes")
        self.assertContains(response, "a problem with the poll")

    def test_quotes_displayed_if_4_quotes_available(self):
        self.create_and_login_user()
        texts = ['COS rocks', 'Jordan rocks', 'Lacey rocks', 'Andrew rocks']
        for text in texts:
            self.create_quote(text=text)
        response = self.client.get(reverse('poll'))
        for text in texts:
            self.assertContains(response, text)

    def test_different_header_messages_displayed_correctly(self):
        self.create_and_login_user()
        initial_response = self.client.get(reverse('poll'))
        self.assertContains(
            initial_response,
            "Try answering one of our polls about your favourite quotes."
        )
        self.assertNotIn(
            "previous answer could not be stored",
            str(initial_response.content)
        )
        self.assertNotIn(
            "answering the previous poll",
            str(initial_response.content)
        )
        my_context = initial_response.context[0].flatten()
        my_context['done'] = True
        template = loader.get_template('polls/poll.html')
        response_content = template.render(my_context)
        self.assertIn(
            "Thank you answering the previous poll. Here is another one!",
            response_content
        )
        self.assertNotIn(
            "previous answer could not be stored", response_content
        )
        self.assertNotIn(
            "Try answering one of our polls", response_content
        )
        my_context['errors'] = True
        response_content = template.render(my_context)
        self.assertIn(
            "Your previous answer could not be stored. Try this one.",
            response_content
        )
        self.assertNotIn(
            "answering the previous poll", response_content
        )
        self.assertNotIn(
            "Try answering one of our polls", response_content
        )

    @patch.object(views, 'PollForm')
    def test_post_method_valid_form(self, mock_poll_form):
        self.create_and_login_user()
        quote = self.create_quote()
        initial_popularity = quote.popularity

        post_data = {'quote_choice': str(quote.id)}

        class FakePollForm(object):

            cleaned_data = post_data

            def is_valid():
                return True

        def side_effect_of_mock(*args, **kwargs):
            return FakePollForm

        mock_poll_form.side_effect = side_effect_of_mock

        response = self.client.post(reverse('poll'), data=post_data)
        form_data = QueryDict('', mutable=True)
        form_data.update(post_data)
        the_call = call(form_data)
        self.assertIn(the_call, mock_poll_form.mock_calls)
        final_popularity = Quote.objects.filter(id=quote.id)[0].popularity
        self.assertEqual(final_popularity, initial_popularity+1)
        self.assertTrue(response.context['done'])

    @patch.object(views, 'PollForm')
    def test_post_method_valid_form(self, mock_poll_form):
        self.create_and_login_user()

        class FakePollForm(object):

            def is_valid():
                return False

        def side_effect_of_mock(*args, **kwargs):
            return FakePollForm

        mock_poll_form.side_effect = side_effect_of_mock
        response = self.client.post(reverse('poll'), data={})
        self.assertTrue(response.context['errors'])


class ProfileViewTest(UserReadyTestCase):

    def test_login_required(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '/login?next=/profile')

    def test_successful_request_with_user_logged_in(self):
        self.create_and_login_user()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_all_post_parameters_are_sensitive(self):
        request = RequestFactory().post('profile', data={})
        response = views.profile(request)
        self.assertEqual(
            request.sensitive_post_parameters,
            '__ALL__'
        )

    def test_never_cache(self):
        self.create_and_login_user()
        request = RequestFactory().get('profile')
        request.user = self.user
        response = views.profile(request)
        self.assertTrue(response.has_header('cache-control'))
        no_cache_headers = [
            'max-age=0', 'no-cache', 'no-store', 'must-revalidate'
        ]
        for header in no_cache_headers:
            self.assertTrue(header in response._headers['cache-control'][1])

    def test_header_displayed_correctly(self):
        self.create_and_login_user()
        response = self.client.get(reverse('profile'))
        header_username = "This is your profile, {}.".format(
            self.username.capitalize()
        )
        self.assertContains(response, header_username)
        self.user.first_name = "Jonny"
        self.user.save()
        response = self.client.get(reverse('profile'))
        self.assertNotIn(header_username, str(response.content))
        header_first_name = "This is your profile, {}.".format(
            self.user.first_name.capitalize()
        )
        self.assertContains(response, header_first_name)

    def test_bottom_links_displayed_correctly(self):
        self.create_and_login_user()
        response = self.client.get(reverse('profile'))
        password_change_url = reverse('password_change')
        password_change_text = "Change password"
        logout_url = reverse('logout')
        logout_text = "Would you like to log out now?"
        self.assertContains(response, password_change_url)
        self.assertContains(response, password_change_text)
        self.assertContains(response, logout_url)
        self.assertContains(response, logout_text)

    def test_form_labels_displayed_correctly(self):
        self.create_and_login_user()
        response = self.client.get(reverse('profile'))
        first_name_label = ProfileForm.base_fields['first_name'].label
        subscribed_label = ProfileForm._meta.labels['subscribed']
        self.assertContains(response, first_name_label)
        self.assertContains(response, subscribed_label)

    @patch.object(Profile.objects, 'create')
    def test_profile_created_on_get_request(self, mock_create_profile):
        self.create_and_login_user()
        self.client.get(reverse('profile'))
        mock_create_profile.assert_called_once()

    @patch.object(Profile.objects, 'filter')
    def test_profile_fetched_not_created_if_exists(self, mock_fetch_profile):
        self.create_user_login_and_profile()
        with patch.object(Profile.objects, 'create') as mock_create_profile:
            self.client.get(reverse('profile'))
            mock_create_profile.assert_not_called()
        mock_fetch_profile.assert_called_with(user=self.user)

    @patch.object(views, 'ProfileForm')
    def test_profileform_called_and_populated_on_get(self, mock_profile_form):
        self.create_user_login_and_profile()
        self.client.get(reverse('profile'))
        mock_profile_form.assert_called()
        form_values = {
            'first_name': self.user.first_name,
            'subscribed': self.profile.subscribed
        }
        mock_profile_form.assert_called_with(form_values)

    @patch.object(views, 'ProfileForm', return_value="This is your form")
    def test_context_rendered_on_get(self, mock_profile_form):
        self.create_user_login_and_profile()
        with patch.object(views.loader, 'get_template') as mock_get_template:
            self.client.get(reverse('profile'))
            context = {
                'profile': self.profile,
                'form': mock_profile_form.return_value,
            }
            call_args = mock_get_template().render.call_args_list[0][0]
            self.assertTrue(context in call_args)

    @patch.object(views, 'ProfileForm')
    def test_profileform_called_and_populated_on_post(self, mock_profile_form):
        post_data = {
            'first_name': 'Jonny',
            'subscribed': False
        }

        class FakeProfileForm(object):
            cleaned_data = post_data

            def is_valid():
                return True

        def side_effect_of_mock(*args, **kwargs):
            return FakeProfileForm
        mock_profile_form.side_effect = side_effect_of_mock
        self.create_user_login_and_profile()
        self.client.post(reverse('profile'), data=post_data)
        mock_profile_form.assert_called()
        call_dict_of_str = mock_profile_form.call_args_list[0][0][0].dict()
        for key in post_data:
            self.assertTrue(key in call_dict_of_str)
            self.assertEqual(str(post_data[key]), call_dict_of_str[key])

    @patch.object(views, 'ProfileForm')
    def test_context_rendered_on_post(self, mock_profile_form):
        class FakeProfileForm(object):
            def is_valid():
                return False

        def side_effect_of_mock(*args, **kwargs):
            return FakeProfileForm

        mock_profile_form.side_effect = side_effect_of_mock

        self.create_user_login_and_profile()
        with patch.object(views.loader, 'get_template') as mock_get_template:
            self.client.post(reverse('profile'))
            context = {
                'profile': self.profile,
                'form': FakeProfileForm,
            }
            call_args = mock_get_template().render.call_args_list[0][0]
            self.assertTrue(context in call_args)

    @patch.object(Profile.objects, 'filter')
    def test_profile_fetched_on_post(self, mock_fetch_profile):
        self.create_user_login_and_profile()
        self.client.post(reverse('profile'))
        mock_fetch_profile.assert_called_with(user=self.user)


class NewUserViewTest(UserReadyTestCase):

    def test_all_post_parameters_are_sensitive(self):
        request = RequestFactory().post('new_user', data={})
        response = views.new_user(request)
        self.assertEqual(
            request.sensitive_post_parameters,
            '__ALL__'
        )

    def test_never_cache(self):
        self.create_and_login_user()
        request = RequestFactory().get('new_user')
        request.user = self.user
        response = views.new_user(request)
        self.assertTrue(response.has_header('cache-control'))
        no_cache_headers = [
            'max-age=0', 'no-cache', 'no-store', 'must-revalidate'
        ]
        for header in no_cache_headers:
            self.assertTrue(header in response._headers['cache-control'][1])

    def test_intro_text_displayed(self):
        response = self.client.get(reverse('new_user'))
        self.assertContains(response, "Input your data to create a new user.")

    def test_form_field_names_displayed(self):
        response = self.client.get(reverse('new_user'))
        form_fields = views.UserForm._meta.fields
        for field_name in form_fields:
            self.assertContains(response, field_name)

    @patch.object(views, 'UserForm')
    def test_UserForm_called_on_get(self, mock_user_form):
        self.client.get(reverse('new_user'))
        mock_user_form.assert_called()

    @patch.object(views, 'UserForm')
    def test_UserForm_called_and_populated_on_post(self, mock_user_form):
        post_data = {
                'username': self.username,
                'email': self.email,
                'password': self.password
            }

        class FakeUserForm(object):
            cleaned_data = post_data

            def is_valid():
                return True

        def side_effect_of_mock(*args, **kwargs):
            return FakeUserForm

        mock_user_form.side_effect = side_effect_of_mock
        self.client.post(reverse('new_user'), data=post_data)
        mock_user_form.assert_called()
        form_data = QueryDict('', mutable=True)
        form_data.update(post_data)
        mock_user_form.assert_called_with(form_data)

    @patch.object(views, 'UserForm')
    def test_logout_called_on_post(self, mock_user_form):
        post_data = {
                'username': self.username,
                'email': self.email,
                'password': self.password
            }

        class FakeUserForm(object):
            cleaned_data = post_data

            def is_valid():
                return True

        def side_effect_of_mock(*args, **kwargs):
            return FakeUserForm

        mock_user_form.side_effect = side_effect_of_mock
        with patch.object(views, 'logout') as mock_logout:
            self.client.post(reverse('new_user'), data=post_data)
            mock_logout.assert_called()

    @patch.object(views, 'UserForm')
    def test_user_created_on_post(self, mock_user_form):
        post_data = {
                'username': self.username,
                'email': self.email,
                'password': self.password
            }

        class FakeUserForm(object):
            cleaned_data = post_data

            def is_valid():
                return True

        def side_effect_of_mock(*args, **kwargs):
            return FakeUserForm

        mock_user_form.side_effect = side_effect_of_mock

        pretend_user = User.objects.create_user(self.username, self.email)
        with patch.object(
            User.objects, 'create_user', return_value=pretend_user
        ) as mock_create_user:
            with patch.object(
                pretend_user, 'set_password'
            ) as mock_set_password:
                with patch.object(
                    pretend_user, 'save'
                ) as mock_save_user:
                    self.client.post(reverse('new_user'), data=post_data)
                    mock_create_user.assert_called_with(
                        self.username, self.email
                    )
                    mock_set_password.assert_called_with(self.password)
                    mock_save_user.assert_called()

    @patch.object(views, 'UserForm')
    def test_login_called_on_post(self, mock_user_form):
        post_data = {
                'username': self.username,
                'email': self.email,
                'password': self.password
            }

        class FakeUserForm(object):
            cleaned_data = post_data

            def is_valid():
                return True

        def side_effect_of_mock(*args, **kwargs):
            return FakeUserForm

        mock_user_form.side_effect = side_effect_of_mock
        with patch.object(views, 'login') as mock_login:
            self.client.post(reverse('new_user'), data=post_data)
            user_just_created = User.objects.filter(username=self.username)[0]
            mock_login.assert_called()
            call_args = mock_login.call_args_list[0][0]
            self.assertIn(user_just_created, call_args)

    @patch.object(views, 'UserForm')
    def test_http_redirect_called_on_post(self, mock_user_form):
        post_data = {
                'username': self.username,
                'email': self.email,
                'password': self.password
            }

        class FakeUserForm(object):
            cleaned_data = post_data

            def is_valid():
                return True

        def side_effect_of_mock(*args, **kwargs):
            return FakeUserForm

        mock_user_form.side_effect = side_effect_of_mock

        # Side effect to be effect of original function in its expected call
        def redirect_side_effect(*args, **kwargs):
            return HttpResponseRedirect('profile')

        with patch.object(views, 'HttpResponseRedirect') as mock_http_redirect:
            mock_http_redirect.side_effect = redirect_side_effect
            self.client.post(reverse('new_user'), data=post_data)
            mock_http_redirect.assert_called_with('profile')

    @patch.object(views, 'UserForm')
    def test_called_function_to_send_welcome_email(self, mock_user_form):
        post_data = {
                'username': self.username,
                'email': self.email,
                'password': self.password
            }

        class FakeUserForm(object):
            cleaned_data = post_data

            def is_valid():
                return True

        def side_effect_of_mock(*args, **kwargs):
            return FakeUserForm

        mock_user_form.side_effect = side_effect_of_mock
        with patch.object(views, 'send_new_user_email') as mock_send_email:
            self.client.post(reverse('new_user'), data=post_data)
            mock_send_email.assert_called_with(self.username, self.email)


class NewUserEmailSenderTest(UserReadyTestCase):
    @patch.object(views, 'EmailMessage')
    def test_email_sent_with_correct_content(self, mock_email_message):
        title = "Welcome, {}!".format(self.username)
        intro = "Welcome to {}{}!\nWe are glad to have you onboard.\n".format(
            "https://", settings.SITE_DOMAIN
        )
        ending = "If you did not just create a user with us, please {}".format(
            "let us know at {} so we can remove your email {}".format(
                settings.EMAIL_HOST_USER, "from our database."
            )
        )
        body = "{}{}".format(intro, ending)
        views.send_new_user_email(self.username, self.email)
        mock_email_message.assert_called_with(title, body, to=[self.email])
        mock_email_message().send.assert_called()

    # The common FakeUserForm and what goes with it should probably go in a
    # separate function as it is used quite a few times


class BaseContentTest(UserReadyTestCase):
    def test_home_in_all_appropriate_pages(self):
        self.create_and_login_user()
        # Missing problematic pages to reverse, like password change and reset
        pages_with_home = [
            'daily', 'random', 'profile', 'login', 'logout', 'new_user',
            'lost_password', 'lost_password_done', 'reset_password_done',
        ]
        for page in pages_with_home:
            response = self.client.get(reverse(page))
            self.assertTrue(response.status_code, 200)
            self.assertContains(response, reverse('index'))
            self.assertContains(response, '<i class="fas fa-home"></i>')

    def test_user_link_in_all_appropriate_pages(self):
        pages_with_user = [
            'index', 'daily', 'random'
        ]
        for page in pages_with_user:
            response = self.client.get(reverse(page))
            self.assertContains(response, reverse('profile'))
            self.assertContains(
                response, "Log in and subscribe to daily quote emails."
            )
        self.create_and_login_user()
        for page in pages_with_user:
            self.user.first_name = ''
            self.user.save()
            response = self.client.get(reverse(page))
            self.assertContains(response, reverse('profile'))
            self.assertContains(
                response,
                "Visit your profile, {}".format(
                    self.user.username.capitalize()
                )
            )
            self.user.first_name = 'Jonny'
            self.user.save()
            response = self.client.get(reverse(page))
            self.assertContains(
                response,
                "Visit your profile, {}".format(
                    self.user.first_name.capitalize()
                )
            )

    def test_common_stylesheets(self):
        self.create_and_login_user()
        # Missing problematic pages to reverse, like password change and reset
        pages_expanding_base = [
            'index', 'daily', 'random', 'profile', 'new_user', 'login',
            'logout', 'lost_password', 'lost_password_done',
            'reset_password_done',
        ]
        for page in pages_expanding_base:
            response = self.client.get(reverse(page))
            self.assertContains(response, 'quotes/style')
            self.assertContains(
                response, 'width=device-width, initial-scale=1.0'
            )
            self.assertContains(response, 'font-awesome.css')
            self.assertContains(response, 'https://use.fontawesome.com')


class LoginViewTest(UserReadyTestCase):
    def test_bottom_links_displayed_correctly(self):
        response = self.client.get(reverse('login'))
        self.assertContains(
            response, 'If you forgot your password, get help here.'
        )
        self.assertContains(response, reverse('lost_password'))
        self.assertContains(
            response, 'Are you a new user? Create an account here.'
        )
        self.assertContains(response, reverse('new_user'))

    def test_form_labels_displayed_correctly(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'Username:')
        self.assertContains(response, 'Password:')

    def test_next_and_no_user_authenticated(self):
        tmp_response = self.client.get(reverse('login'))
        my_context = tmp_response.context[0].flatten()
        my_context['next'] = True
        template = loader.get_template('user/login.html')
        response_content = template.render(my_context)
        self.assertIn(
            'Please login to see this page.',
            response_content
        )

    def test_next_and_user_authenticated(self):
        self.create_and_login_user()
        tmp_response = self.client.get(reverse('login'))
        my_context = tmp_response.context[0].flatten()
        my_context['next'] = True
        template = loader.get_template('user/login.html')
        response_content = template.render(my_context)
        message = "Your account doesn't have access to this page. {}".format(
            "To proceed, please login with an account that has access."
        )
        self.assertIn(
            message,
            response_content
        )

    def test_form_errors(self):
        class FakeFormClass(object):
            errors = True
        tmp_response = self.client.post(reverse('login'))
        my_context = tmp_response.context[0].flatten()
        my_context['form'] = FakeFormClass
        template = loader.get_template('user/login.html')
        response_content = template.render(my_context)
        self.assertIn(
            "Your username and password didn't match. Please try again.",
            response_content
        )


class LogoutViewTest(UserReadyTestCase):

    def test_header_displayed(self):
        response = self.client.get(reverse('logout'))
        self.assertContains(response, 'You are now logged out.')

    def test_login_link_displayed(self):
        response = self.client.get(reverse('logout'))
        self.assertContains(response, reverse('login'))
        self.assertContains(response, 'Log in again')


class LostPasswordViewTest(TestCase):
    def test_header_displayed(self):
        response = self.client.get(reverse('lost_password'))
        header_str = 'Enter your email address below to receive {}'.format(
            'an email with instructions for setting a new password.'
        )
        self.assertContains(
            response,
            header_str
        )

    def test_submit_displayed(self):
        response = self.client.get(reverse('lost_password'))
        self.assertContains(
            response,
            '<input type="submit" value="Reset my password">'
        )

    def test_form_label_displayed(self):
        response = self.client.get(reverse('lost_password'))
        self.assertContains(
            response,
            "Email"
        )


class LostPasswordDoneViewTest(TestCase):
    def test_text_content_displayed(self):
        response = self.client.get(reverse('lost_password_done'))
        self.assertContains(
            response,
            "We've emailed you instructions for setting your password."
        )
        longer_text = "If you don't receive an email, make sure {}".format(
            "you've entered the address correctly and check your spam folder."
        )
        self.assertContains(
            response,
            longer_text
        )


class ResetPasswordViewTest(TestCase):

    def test_header_displayed(self):
        tmp_response = self.client.get(reverse(
            'reset_password', kwargs={
                'uidb64': 'Nw',
                'token': '4w3-813b21d8950ad39c5f28'
            }
        ))
        my_context = tmp_response.context[0].flatten()
        my_context['validlink'] = True
        template = loader.get_template('user/reset_password.html')
        response_content = template.render(my_context)
        self.assertIn(
            'Please enter your new password twice below.', response_content
        )
        self.assertNotIn(
            'The password reset link is invalid', response_content
        )

    def test_link_invalid(self):
        tmp_response = self.client.get(reverse(
            'reset_password', kwargs={
                'uidb64': 'Nw',
                'token': '4w3-813b21d8950ad39c5f28'
            }
        ))
        my_context = tmp_response.context[0].flatten()
        my_context['validlink'] = False
        template = loader.get_template('user/reset_password.html')
        response_content = template.render(my_context)
        self.assertIn(
            'The password reset link is invalid, it may have already been used',
            response_content
        )
        self.assertIn(
            'Please request a new password reset.',
            response_content
        )
        self.assertNotIn(
            'Please enter your new password twice below.',
            response_content
        )


class ResetPasswordDoneViewTest(TestCase):
    def test_header_displayed(self):
        response = self.client.get(reverse('reset_password_done'))
        self.assertContains(response, 'Your new password has been set.')

    def test_login_link_displayed(self):
        response = self.client.get(reverse('reset_password_done'))
        self.assertContains(response, 'Log in')
        self.assertContains(response, reverse('login'))


class PasswordChangeViewTest(UserReadyTestCase):
    def test_intro_text_displayed(self):
        self.create_and_login_user()
        response = self.client.get(reverse('password_change'))
        self.assertContains(
            response,
            "Please enter your old password and then your new password twice."
        )

    def test_form_labels_displayed(self):
        self.create_and_login_user()
        response = self.client.get(reverse('password_change'))
        self.assertContains(response, 'Old password:')
        self.assertContains(response, 'New password:')
        self.assertContains(response, 'New password confirmation:')

    def test_input_button_displayed(self):
        self.create_and_login_user()
        response = self.client.get(reverse('password_change'))
        self.assertContains(
            response,
            '<input type="submit" value="Change my password" class="default">'
        )

    def test_form_and_errors_displayed(self):
        class FakeField(object):
            errors = "error"
            label_tag = "label"

            def __str__(self):
                return "{}name".format(self.label_tag[:-5])

            def generate_fields(self, tag):
                self.errors = "{} {}".format(tag, self.errors)
                self.label_tag = "{} {}".format(tag, self.label_tag)
                self.__str__()

        class FakeFormClass(object):
            old_password = FakeField()
            new_password1 = FakeField()
            new_password2 = FakeField()
            errors = {"error": "An error"}
        tags = {
            'old': "Old password",
            'new1': "New password",
            'new2': "New password confirmation"
        }
        FakeFormClass.old_password.generate_fields(tags['old'])
        FakeFormClass.new_password1.generate_fields(tags['new1'])
        FakeFormClass.new_password2.generate_fields(tags['new2'])

        self.create_and_login_user()
        tmp_response = self.client.get(reverse('password_change'))
        my_context = tmp_response.context[0].flatten()
        my_context['form'] = FakeFormClass
        template = loader.get_template('user/password_change.html')
        response_content = template.render(my_context)
        self.assertIn("Please correct the error(s) below.", response_content)
        for key in tags:
            self.assertIn("{} error".format(tags[key]), response_content)
            self.assertIn("{} label".format(tags[key]), response_content)
            self.assertIn("{} name".format(tags[key]), response_content)


class PasswordChangeDoneViewTest(UserReadyTestCase):
    def test_header_displayed_correctly(self):
        self.create_and_login_user()
        response = self.client.get(reverse('password_change_done'))
        self.assertContains(
            response,
            "Your password has been changed!"
        )

    def test_link_displayed_correctly(self):
        self.create_and_login_user()
        response = self.client.get(reverse('password_change_done'))
        self.assertContains(
            response,
            "Go to your profile"
        )
        self.assertContains(
            response,
            reverse('profile')
        )
