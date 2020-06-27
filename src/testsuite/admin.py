from django.contrib import admin

from testsuite.forms import TestForm, QuestionsInlineFormSet, AnswerInlineFormSet
from testsuite.models import Test, Question, Topic, Answer

admin.site.register(Topic)
# admin.site.register(Question)


class QuestionsInline(admin.TabularInline):
    model = Question
    fields = ('text', 'number')  # 'num_variant_min_limit')
    show_change_link = True
    extra = 0
    formset = QuestionsInlineFormSet


class AnswersInline(admin.TabularInline):
    model = Answer
    fields = ('text', 'is_correct',)  # 'num_variant_min_limit')
    show_change_link = True
    extra = 0
    formset = AnswerInlineFormSet


class TestAdminModel(admin.ModelAdmin):
    fields = ('title', 'description', 'level', 'image', 'topic')
    list_display = ('title', 'description', 'level', 'image', 'topic')
    list_per_page = 10
    inlines = (QuestionsInline,)
    form = TestForm
    formset = QuestionsInlineFormSet


class QuestionAdminModel(admin.ModelAdmin):
    # fields = ('question', 'answer')
    list_display = ('number', 'text', 'description', 'test')
    list_select_related = ('test',)
    list_per_page = 10
    inlines = (AnswersInline,)


admin.site.register(Test, TestAdminModel)
admin.site.register(Question, QuestionAdminModel)
