from testsuite.views import TestSuiteListView
from django.urls import path

from user_account.views import CreateUserAccountView, SuccessRegistrationView, UserAccountLoginView, \
    UserAccountLogoutView, UserAccountUpdateView, user_account_profile

app_name = 'user_account'

urlpatterns = [
    path('register/', CreateUserAccountView.as_view(), name='registration'),
    path('success-registration/', SuccessRegistrationView.as_view(), name='success-registration'),
    path('login/', UserAccountLoginView.as_view(), name='login'),
    path('logout/', UserAccountLogoutView.as_view(), name='logout'),
    path('profile/', user_account_profile, name='profile'),

]
