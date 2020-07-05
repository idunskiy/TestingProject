import datetime

from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse

from testsuite.models import Test, Question


class TestModelTest(TestCase):

    def setUp(self):
        call_command('loaddata', 'tests/fixtures/user_account.json', verbosity=0)
        call_command('loaddata', 'tests/fixtures/tests.json', verbosity=0)

    def tearDown(self):
        pass

    def test_question_count(self):
        test = Test.objects.create(title='Test title')
        count = test.question_count()
        question = Question.objects.create(
            test=test,
            number=1,
            text='Question text'
        )
        self.assertEqual(test.question_count(), count + 1)

    def test_last_run(self):

        test = Test.objects.first()
        dt = datetime.datetime.strptime('2020-07-05T07:46:36.743Z', "%Y-%m-%dT%H:%M:%S.%f%z")
        self.assertEqual(test.last_run(), dt)


class UrlsAvailabilityTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_public_url(self):
        urls = [
            (reverse('index'), 'Welcome to TMB!'),
            (reverse('test:list'), 'Test list'),
        ]
        for url, content in urls:
            response = self.client.get(url)
            assert response.status_code == 200
            assert content in response.content.decode()

    def test_private_urls(self):
        private_urls = [
            reverse('leaderboard'),
        ]
        for url in private_urls:
            response = self.client.get(url)
            self.assertRedirects(response, '{}?next={}'.format(reverse('login'), url))