from django import template
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max, Sum, Count


from testsuite.models import TestResult


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    image = models.ImageField(default='pics/default.jpg', upload_to='pics')

    def best_result(self):
        result = TestResult.objects.filter(user__pk=self.id).aggregate(
            max_score=Max('avg_score')
        )
        if result['max_score'] is not None:
            return round(result['max_score'], 2)

    def last_test_run(self):
        latest_test_result = TestResult.objects.filter(user__pk=self.id).latest('datetime_run')
        return latest_test_result.datetime_run

    def score_total(self):
        result = TestResult.objects.filter(user__pk=self.id).aggregate(
            sum_score=Sum('avg_score')
        )
        if result['sum_score'] is not None:
            return round(result['sum_score'], 2)

    def percentage_of_successful_runs(self):
        all_test_results = self.test_results.all()
        successful_tests = 0
        for test_result in all_test_results:
            if test_result.all_questions().count() is not 0:
                if test_result.correct_answers_count() / test_result.all_questions().count() == 1:
                    successful_tests += 1
        if all_test_results.count() != 0:
            return round(successful_tests / all_test_results.count() * 100, 2)
        # return '0'
