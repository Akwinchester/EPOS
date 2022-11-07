from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import ListView, CreateView, DetailView
from .models import tasks
from .forms import Register_User
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout



class HomePage(ListView):
    model = tasks

    context_object_name = 'tasks'
    template_name = 'app_reminders/home_page.html'


# class ProfilePage(DetailView):
#     model = Profile
#     template_name = 'base/user_profile.html'
#
#     def get_context_data(self, *args, **kwargs):
#         users = Profile.objects.all()
#         context = super(ShowProfilePageView, self).get_context_data(*args, **kwargs)
#         page_user = get_object_or_404(Profile, id=self.kwargs['pk'])
#         context['page_user'] = page_user
#         return context


class AddUser(CreateView):
    form_class = Register_User
    template_name = 'app_reminders/add_user.html'
    success_url = reverse_lazy('List_deck_category', args = ['all'])
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(reverse_lazy('Home_page'))


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'app_reminders/login_user.html'
    def get_success_url(self):
        return reverse_lazy('Home_page')


def logout_user(request):
    logout(request)
    return redirect('Login_user')