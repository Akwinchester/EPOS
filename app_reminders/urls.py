from django.urls import path
from .views import HomePage, AddUser, LoginUser, logout_user, ProfilePage, CreateProfilePage, Post

urlpatterns = [
    path('home_page/', HomePage.as_view(), name='Home_page'),
    path('add_user/', AddUser.as_view(), name='Add_user'),
    path('login_user', LoginUser.as_view(), name='Login_user'),
    path('logout/', logout_user, name='Logout_user'),
    path('profile/<int:pk>/', ProfilePage.as_view(), name='Profile_user'),
    path('create_profile/',CreateProfilePage.as_view(), name='Create_profile_user'),
    path('post/', Post, name='Post'),
]