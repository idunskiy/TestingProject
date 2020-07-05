from django.urls import path

from testsuite.views import TestRunView, TestSuiteListView, TestDeleteView, TestStartView

app_name = 'test'

urlpatterns = [

    path('', TestSuiteListView.as_view(), name='list'),
    path('delete/<int:pk>', TestDeleteView.as_view(), name='delete'),
    path('<int:pk>/start/', TestStartView.as_view(), name='start'),
    # path('<int:pk>/question/<int:seq_nr>', TestRunView.as_view(), name='testrun_step'),
    path('<int:pk>/next', TestRunView.as_view(), name='next'),

]