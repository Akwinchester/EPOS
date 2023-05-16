from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from .models import tasks, Profile
from .forms import Register_User
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from datetime import datetime, timedelta



import json


class HomePage(ListView):
    model = tasks

    context_object_name = 'tasks'
    template_name = 'app_reminders/tasks.html'

    def get_queryset(self):
        qs = super().get_queryset()
        print(qs)
        print(qs.filter(user=self.request.user))
        qs = qs.filter(id=214)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # user = User.objects.create_user('user_from_code_1', password='123ewqasdCXZ')

        tasks_object = tasks.objects.filter(user=self.request.user)
        list_data = []
        for  i in range(0,len(tasks_object)):
            print(tasks_object[i].deadline)
            list_data.append({"id":tasks_object[i].id_time, "text": tasks_object[i].task_text, "done":tasks_object[i].status, "date":f"{tasks_object[i].deadline.year}-{tasks_object[i].deadline.month}-{tasks_object[i].deadline.day+1}"})

        tasks_object = str(list_data)
        tasks_object = tasks_object.replace('False', 'false')
        tasks_object = tasks_object.replace('True', 'true')
        tasks_object = tasks_object.replace("'",'"')
        context['task_for_js'] = tasks_object
        return context


def Post(request):
    if request.method == "POST":
        dict_from_js = json.loads(request.body.decode())
        if dict_from_js['date']=="":
            new_task = tasks(task_text=dict_from_js['text'], status=dict_from_js['done'], id_time=dict_from_js['id'], user=request.user)
        else:
            new_task = tasks(task_text=dict_from_js['text'], status=dict_from_js['done'], id_time=dict_from_js['id'], deadline=dict_from_js['date'], user=request.user)

        new_task.save()

    return HttpResponse('ответ от Post')


def Post_status(request):
    if request.method == "POST":
        dict_from_js = json.loads(request.body.decode())
        task = tasks.objects.get(id_time=dict_from_js['id'])
        task.status = dict_from_js['status']
        task.save()
    return HttpResponse('ответ от Post_status')


def Post_delete(request):
    if request.method =="POST":
        task_id = request.body.decode()
        print(task_id)
        tasks.objects.get(id_time=task_id).delete()

    return HttpResponse('ответ от Post_delete')



class ProfilePage(DetailView):
    model = Profile
    template_name = 'app_reminders/profile.html'

    def get_context_data(self, *args, **kwargs):
        users = Profile.objects.all()
        context = super(ProfilePage, self).get_context_data(*args, **kwargs)
        page_user = get_object_or_404(Profile, id=self.kwargs['pk'])
        context['page_user'] = page_user
        return context


class CreateProfilePage(CreateView):
    model = Profile

    template_name = 'app_reminders/create_profile.html'
    fields = ['profile_pic', 'bio', 'facebook', 'twitter', 'instagram']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return redirect(reverse_lazy('Home_page'))

    success_url = reverse_lazy('Home_page')


class AddUser(CreateView):
    form_class = Register_User
    template_name = 'app_reminders/add_user.html'
    success_url = reverse_lazy('List_deck_category', args = ['all'])
    def form_valid(self, form):
        profile_user = Profile()
        profile_user.user = self.request.user.id
        profile_user.save()
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