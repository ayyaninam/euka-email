from django.contrib import admin
from django.urls import path
from . import views

app_name = "base"

urlpatterns = [
    path('add-user-email', views.add_user_email, name="add_user_email"),
    path('get-user-emails/<str:user_id>/<str:condition>', views.get_user_emails, name="get_user_emails"),
]
