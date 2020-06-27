from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView

from user_account.forms import UserAccountRegistrationForm, UserAccountProfileForm, UserProfileUpdateForm
from user_account.models import User


class CreateUserAccountView(CreateView):
    model = User
    template_name = 'registration.html'
    form_class = UserAccountRegistrationForm

    def get_success_url(self):
        return reverse('user_account:success-registration')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['title'] = 'Register new user'
        return context


class SuccessRegistrationView(TemplateView):
    template_name = 'success.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['title'] = 'Successfully created a user'
        messages.success(self.request, f'Your account has been created!')
        return context


class UserAccountLoginView(LoginView):
    template_name = 'login.html'
    extra_context = {'title': 'Login as a user'}
    success_url = reverse_lazy('index')


class UserAccountLogoutView(LogoutView):
    template_name = 'logout.html'
    extra_context = {'title': 'Logout from LMS'}


class UserAccountUpdateView(UpdateView):
    template_name = 'profile.html'
    extra_context = {'title': 'Edit current user profile.'}
    form_class = UserAccountProfileForm

    def get_object(self):
        return self.request.user


@login_required
def user_account_profile(request):
    if request.method == 'POST':
        u_form = UserAccountProfileForm(request.POST, instance=request.user)
        p_form = UserProfileUpdateForm(request.POST,
                                       request.FILES,
                                       instance=request.user)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('user_account:profile')

    else:
        u_form = UserAccountProfileForm(instance=request.user)
        p_form = UserProfileUpdateForm(instance=request.user)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title': f'Edit {request.user.get_full_name()} user profile'
    }

    return render(
        request=request,
        template_name='profile.html',
        context=context
    )