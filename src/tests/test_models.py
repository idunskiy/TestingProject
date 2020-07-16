import datetime
import random
import string
from collections import OrderedDict

from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse
from faker import Faker

from testsuite.models import Test, Question, TestResult


class TestModelTest(TestCase):

    def setUp(self):
        call_command('loaddata', 'tests/fixtures/user_account.json', verbosity=0)
        call_command('loaddata', 'tests/fixtures/testsuite.json', verbosity=0)

    def tearDown(self):
        pass

    def test_questions_count(self):
        test = Test.objects.create(title='Test title')
        count = test.questions_count()
        question = Question.objects.create(
            test=test,
            number=1,
            text='Question text'
        )
        self.assertEqual(test.questions_count(), count + 1)


class TestUrlsAvailabilityTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_public_url(self):
        urls = [
            (reverse('index'), 'Welcome to Tests System!'),
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
            self.assertRedirects(response, '{}?next={}'.format(reverse('user_account:login'), url))


class AccountExtendedTests(TestCase):

    fake = Faker()
    CREDENTIALS = {
        'username': 'unit_test',
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'password1': 'zxcvfdsa',
        'password2': 'zxcvfdsa',
    }

    def setUp(self):
        self.client = Client()
        call_command('loaddata', 'tests/fixtures/user_account.json', verbosity=0)
        call_command('loaddata', 'tests/fixtures/testsuite.json', verbosity=0)

    def test_account_public_url(self):
        urls = [
            (reverse('user_account:login'), 'Login as a user'),
            (reverse('user_account:registration'), 'Register new user'),
        ]
        for url, content in urls:
            response = self.client.get(url)
            assert response.status_code == 200
            assert content in response.content.decode()

    def test_account_registration(self):
        url = reverse('user_account:registration')
        self.client.post(url, self.CREDENTIALS)
        self.client.login(username=self.CREDENTIALS['username'], password=self.CREDENTIALS['password1'])
        response = self.client.get(reverse('user_account:profile'))
        assert response.status_code == 200
        assert 'Edit' in response.content.decode()


class TestModelExtendedTests(TestCase):

    def setUp(self):
        call_command('loaddata', 'tests/fixtures/user_account.json', verbosity=0)
        call_command('loaddata', 'tests/fixtures/testsuite.json', verbosity=0)
        self.client = Client()
        self.client.login(username='gordon', password='zxcvfdsa')

    def _run_test(self, test):
        self.client.get(reverse('test:start', kwargs={'pk': test.id}))
        next_url = reverse('test:next', kwargs={'pk': test.id})
        for step in range(1, test.questions_count()+1):
            self.client.get(next_url)
            self.client.post(
                path=next_url,
                data={
                    'answer_1': "1"
                }
            )

    def _run_test_with_answers(self, test, *args):
        self.client.get(reverse('test:start', kwargs={'pk': test.id}))
        next_url = reverse('test:next', kwargs={'pk': test.id})
        for idx, step in enumerate(range(1, test.questions_count() + 1), 1):
            self.client.get(next_url)
            response = self.client.get(next_url)
            assert response.status_code == 200
            self.client.post(
                    path=next_url,
                    data={
                        '{}'.format(args[0][idx - 1]): "1"
                    }
                )

    def test_last_run(self):
        test = Test.objects.first()
        utc_now = datetime.datetime.now(tz=datetime.timezone.utc)

        prev_last_run = test.last_run()
        self._run_test(test)
        new_last_run = test.last_run()

        self.assertLess(prev_last_run, new_last_run)
        self.assertLess(utc_now, new_last_run)

    def test_pass_success(self):
        # Math test
        test = Test.objects.get(pk=1)
        answers = 'answers_1', 'answers_3', 'answers_3'
        self._run_test_with_answers(test, answers)
        test_result = test.test_results.order_by('-id').first()
        self.assertEqual(test_result.correct_answers_count(), 3)

    def test_pass_fail(self):
        # Chemistry test
        test = Test.objects.get(pk=2)
        answers = 'answers_2', 'answers_3', 'answers_2'
        self._run_test_with_answers(test, answers)
        test_result = test.test_results.order_by('-id').first()
        self.assertNotEqual(test_result.correct_answers_count(), 3)
