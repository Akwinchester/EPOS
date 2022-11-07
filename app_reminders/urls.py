from django.urls import path
from .views import HomePage, AddUser, LoginUser, logout_user

urlpatterns = [
    path('home_page/', HomePage.as_view(), name='Home_page'),
    path('add_user/', AddUser.as_view(), name='Add_user'),
    path('login_user', LoginUser.as_view(), name='Login_user'),
    path('logout/', logout_user, name='Logout_user'),
    path('profile/', )
]