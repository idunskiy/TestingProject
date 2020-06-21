from django.contrib import admin

from testsuite.models import Test, Question

admin.site.register(Test)


class QuestionsInline(admin.TabularInline):
    model = Question
    fields = ('text',)  # 'num_variant_min_limit')
    show_change_link = True
    extra = 1


class TestAdminModel(admin.ModelAdmin):
    fields = ('title', 'description', 'level', 'image')
    list_display = ('title', 'description', 'level', 'image')
    list_per_page = 10
    inlines = (QuestionsInline,)
