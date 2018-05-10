import copy
from django.conf import settings
from django.contrib.auth.models import User
from django.http import QueryDict, HttpResponseRedirect
from django.urls import reverse
from django.test import TestCase, RequestFactory
from mock import patch
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

    # The common FakeUserForm and what goes with it should probably go in a
    # separate function as it is used quite a few times


class BaseContentTest(TestCase):
    def test_home_in_all_appropriate_pages(self):
        pages_with_home = [
            'daily', 'random', 'profile', 'login', 'logout'
        ]  # ...
        pass
