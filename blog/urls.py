from django.urls import path
from . import views

urlpatterns = [
    path("", views.loginPage, name="login"),
    path("create-account", views.create_account, name="create-account"),
    path("new", views.new, name="new"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("delete/<str:title>", views.delete, name="delete"),
    path("save", views.save, name="save"),
    path("logout", views.logoutUser, name="logout"),
    path("home", views.home, name="home"),
    path("<str:title>", views.post, name="user_post")
]