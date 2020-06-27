from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Count, Sum

from app import settings


class Topic(models.Model):

    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return f'{self.title} + {self.description}'


class Test(models.Model):
    MIN_LIMIT = 3
    MAX_LIMIT = 20

    LEVEL_CHOICES = (
        (1, 'Basic'),
        (2, 'Middle'),
        (3, 'Advanced'),
    )
    topic = models.ForeignKey(to=Topic, related_name='tests', null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1024, null=True, blank=True)
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=2)
    image = models.ImageField(default='pics/default.jpg', upload_to='pics')

    def __str__(self):
        return f'{self.title} , {self.topic}, {self.description}, {self.level}'

    def question_count(self):
        return self.questions.count()

    def last_run(self):
        last_run = self.test_suite_runs.order_by('-id').first()
        if last_run:
            return last_run.datetime_run
        return ''


class Question(models.Model):
    MIN_LIMIT = 3
    MAX_LIMIT = 6
    number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(MAX_LIMIT)])
    test = models.ForeignKey(to=Test, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=64)
    description = models.TextField(max_length=512, null=True, blank=True)

    def __str__(self):
        return f'{self.text}'

    def next(self):
        return 'next'

    def prev(self):
        return 'prev'


class Answer(models.Model):
    text = models.CharField(max_length=64)
    question = models.ForeignKey(to=Question, related_name='answers', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.text}'


class TestResult(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='test_results', on_delete=models.CASCADE)
    test = models.ForeignKey(to=Test, related_name='test_results', on_delete=models.CASCADE)
    avg_score = models.DecimalField(default=0, decimal_places=2, max_digits=5, validators=[MinValueValidator(0),
                                                                                           MaxValueValidator(100)])
    datetime_run = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def update_score(self):
        qs = self.test_result_details.values('question').annotate(
            num_answers=Count('question'),
            points=Sum('is_correct')
        )
        self.score = sum(
            entry['num_answers'] == int(entry['points'])
            for entry in qs
        )

    def finish(self):
        self.update_score()
        self.is_completed=True


class TestResultDetail(models.Model):
    test_result = models.ForeignKey(to=TestResult, related_name='test_result_details', on_delete=models.CASCADE)
    question = models.ForeignKey(to=Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(to=Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
