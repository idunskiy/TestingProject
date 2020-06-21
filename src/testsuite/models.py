from django.db import models

from app import settings


class Topic(models.Model):

    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return f'{self.title} + {self.description}'


class Test(models.Model):

    LEVEL_CHOICES = (
        (1, 'Basic'),
        (2, 'Middle'),
        (3, 'Advanced'),
    )
    topic = models.ForeignKey(to=Topic, related_name='tests', null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1024, null=True, blank=True)
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=2)
    image = models.ImageField(default='default.png', upload_to='covers')

    def __str__(self):
        return f'{self.title}'


class Question(models.Model):
    MIN_LIMIT = 3
    MAX_LIMIT = 6

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
    correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.text}'


class TestResult:
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='test_results', on_delete=models.CASCADE)
    test = models.ForeignKey(to=Test, related_name='test_results', on_delete=models.CASCADE)
    avg_score = models.DecimalField(max_digits=6, decimal_places=2)