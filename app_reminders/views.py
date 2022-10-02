from django.shortcuts import render, HttpResponse
from django.views.generic import ListView
from .models import tasks


class HomePage(ListView):
    model = tasks
    context_object_name = 'tasks'
    template_name = 'app_reminders/home_page.html'