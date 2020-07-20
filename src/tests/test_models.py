import datetime
import random
import string
from collections import OrderedDict

from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse
from faker import Faker

from testsuite.models import Test, Question, TestResult, Answer


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

    def _run_test_with_answers(self, test, correct_answers=None):
        self.client.get(reverse('test:start', kwargs={'pk': test.id}))
        next_url = reverse('test:next', kwargs={'pk': test.id})
        for idx, step in enumerate(range(1, test.questions_count() + 1), 1):
            self.client.get(next_url)
            response = self.client.get(next_url)
            assert response.status_code == 200
            _correct_answer = correct_answers.get('{}'.format(idx))
            self.client.post(
                    path=next_url,
                    data={
                        _correct_answer: "1"
                    }
                )

    def _correct_answers(self, test: Test):
        correct_answers = dict()
        for question_idx, question in enumerate(test.questions.all(), 1):
            answers = Answer.objects.filter(question_id=question.id).select_related('question').all()
            for answer_idx, answer in enumerate(list(answers), 1):
                if answer.is_correct:
                    correct_answers['{}'.format(question_idx)] = 'answers_'+'{}'.format(answer_idx)
        return correct_answers

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
        self._run_test_with_answers(test, self._correct_answers(test))
        test_result = test.test_results.order_by('-id').first()
        self.assertEqual(test_result.correct_answers_count(), 3)


    def test_pass_fail(self):
        # Chemistry test
        test = Test.objects.get(pk=2)
        incorrect_answers = self._correct_answers(test)
        index = random.randint(1, len(incorrect_answers))
        chosen_answer = incorrect_answers.get('{}'.format(index))
        new_value = int(chosen_answer[len('answers_'):])+1
        incorrect_answer = 'answers_' + '{}'.format(new_value)
        incorrect_answers['{}'.format(index)] = incorrect_answer
        self._run_test_with_answers(test, incorrect_answers)
        test_result = test.test_results.order_by('-id').first()
        self.assertNotEqual(test_result.correct_answers_count(), 3)
