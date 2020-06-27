import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView

from testsuite.forms import TestDeleteForm
from testsuite.models import Question, Test, Answer, TestResultDetail, TestResult
from user_account.models import User


class TestSuiteListView(ListView):
    model = Test
    template_name = 'tests_list.html'
    context_object_name = 'tests_list'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('-id')
        print(qs)

        return qs


class LeaderBoardView(ListView):
    model = User
    template_name = 'leaderboard.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('-id')
        print(qs)

        return qs


class TestDeleteView(DeleteView):
    model = Test
    form_class = TestDeleteForm

    def get_success_url(self):
        return reverse('test:list')


class TestRunView(View):
    PREFIX = 'answers_'

    def get(self, request, pk, seq_nr):
        question = Question.objects.all().filter(test__id=pk, number=seq_nr).first()
        answers = [
            answer.text
            for answer in question.answers.all()
        ]

        return render(
            request=request,
            template_name='testrun.html',
            context={
                'question': question,
                'answers': answers,
                'prefix': self.PREFIX
            }
        )

    def post(self, request, pk, seq_nr):
        test = Test.objects.get(pk=pk)
        question = Question.objects.filter(test__id = pk, number=seq_nr).first()
        data = request.POST
        answers = Answer.objects.filter(
            question = question
        ).all()
        data = request.POST
        choices = {
            k: True
            for k in request.POST if k.startswith(self.PREFIX)
        }

        if not choices:
            messages.error(self.request, extra_tags = 'danger', )
            return redirect(reverse('test:testrun_step', kwargs={'pk': pk, 'seq_nr':seq_nr}))

        current_test_result = TestResult.objects.filter(
            test=test,
            user=request.user,
            is_completed=False
        ).last()

        for idx, answer in enumerate(answers, 1):
           value = choices.get(str(idx), False)
           test_result_detail = TestResultDetail.objects.create(
               test_result=current_test_result,
               question=question,
               answer=answer,
               is_correct=(value == answer.is_correct)
           )

        if question.number < test.question_count():
            return redirect(reverse('test:testrun_step', kwargs={'pk': pk, 'seq_nr': seq_nr + 1}))
        else:
            current_test_result.finish()
            current_test_result.save()
            return render(
                request=request,
                template_name='testrun_end.html',
                context={
                    'test_result': current_test_result,
                    'time_spent': datetime.datetime.utcnow() - current_test_result.datetime_run.replace(tzinfo=None)
                }
                )

        return redirect(reverse('test:testrun_step', kwargs={'pk': pk, 'seq_nr':seq_nr+1}))


# class TestSuiteListView(ListView):
#     model = Test
#     template_name = ''
