import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader, Context
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
    login_url = reverse_lazy('user_account:login')

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('-id')
        print(qs)

        return qs


class TestStartView(LoginRequiredMixin, View):
    model = Test
    login_url = reverse_lazy('user_account:login')

    def get(self, request, pk):
        test = Test.objects.get(pk=pk)

        test_result_id = request.session.get('testresult')

        if test_result_id:
            test_result = TestResult.objects.get(id=test_result_id)
        else:
            test_result = TestResult.objects.create(
                user=request.user,
                test=test
            )
        request.session['testresult'] = test_result.id
        best_result = test.best_result()

        number_of_runs = test_result.test_runs_count()
        print('number of all runs' + str(number_of_runs))
        return render(
            request=request,
            template_name='test_before_start.html',
            context={
                'best_result': best_result,
                'test': test,
                'test_result': test_result
            }
        )


class LeaderBoardView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'leaderboard.html'
    context_object_name = 'users_list'
    login_url = reverse_lazy('user_account:login')

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('-id')
        print(qs)

        return qs


class TestDeleteView(LoginRequiredMixin, DeleteView):
    model = Test
    form_class = TestDeleteForm
    login_url = reverse_lazy('user_account:login')

    def get_success_url(self):
        return reverse('test:list')


class TestRunView(LoginRequiredMixin, View):
    PREFIX = 'answers_'
    login_url = reverse_lazy('user_account:login')

    def get(self, request, pk):

        if 'testresult' not in request.session:
            return HttpResponse('Error')

        testresult_step = request.session.get('testresult_step', 1)
        request.session['testresult_step'] = testresult_step
        question = Question.objects.get(test__id=pk, number=testresult_step)
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

    def post(self, request, pk):

        if ('testresult') not in request.session:
            return HttpResponse('Error')
        testresult_step = request.session.get('testresult_step', 1)

        test = Test.objects.get(pk=pk)
        question = Question.objects.get(test__id=pk, number=testresult_step)
        answers = Answer.objects.filter(
            question=question
        ).all()

        choices = {
            k.replace(self.PREFIX, ''): True
            for k in request.POST if k.startswith(self.PREFIX)
        }

        if not choices:
            messages.error(self.request, extra_tags='danger', message='ERROR: You should select at least 1 answer!')
            return redirect(reverse('test:next', kwargs={'pk': pk}))

        if len(choices) == len(answers):
            messages.error(self.request, extra_tags='danger', message=f"ERROR: You can't select all answers!")
            return redirect(reverse('test:next', kwargs={'pk': pk}))

        print('testresult in post' + str(request.session['testresult']))
        current_test_result = TestResult.objects.get(
            id=request.session['testresult']
        )
        for idx, answer in enumerate(answers, 1):
           value = choices.get(str(idx), False)
           TestResultDetail.objects.create(
               test_result=current_test_result,
               question=question,
               answer=answer,
               is_correct=(value == answer.is_correct)
           )

        if question.number < test.questions_count():
            current_test_result.is_new = False
            current_test_result.save()
            request.session['testresult_step'] = testresult_step + 1
            return redirect(reverse('test:next', kwargs={'pk': pk}))
        else:
            del request.session['testresult_step']
            del request.session['testresult']
            current_test_result.finish()
            current_test_result.save()

            dt1 = datetime.datetime.utcnow().replace(microsecond=0)
            dt2 = current_test_result.datetime_run.replace(tzinfo=None, microsecond=0)
            best_result = test.best_result()
            return render(
                request=request,
                template_name='testrun_end.html',
                context={
                    'best_result': best_result,
                    'test_result': current_test_result,
                    'time_spent': str(dt1-dt2)
                }
                )


def handler404(request, exception):
    # 1. Load models for this view
    # from idgsupply.models import My404Method

    # 2. Generate Content for this view
    template = loader.get_template('404.html')
    context = Context({
        'message': 'All: %s' % request,
    })

    # 3. Return Template for this view + Data
    return HttpResponse(content=template.render(context), content_type='text/html; charset=utf-8', status=404)


def handler500(request):
    # 1. Load models for this view
    # from idgsupply.models import My404Method

    # 2. Generate Content for this view
    template = loader.get_template('500.html')
    context = Context({
        'message': 'All: %s' % request,
    })

    # 3. Return Template for this view + Data
    return HttpResponse(content=template.render(context), content_type='text/html; charset=utf-8', status=500)


# def last_run(self):
#         last_run = self.test_runs.order_by('-id').first()
#         if last_run:
#             return last_run.datetime_run
#         return ''
#
#     datetime_run = models.DateTimeField(auto_now_add=True)
#     is_completed = models.BooleanField(default=False)

