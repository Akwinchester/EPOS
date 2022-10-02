from django.urls import path
from .views import HomePage

urlpatterns = [
    path('home_page/', HomePage.as_view(), name='Home_page')
]