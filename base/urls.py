from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "base"

urlpatterns = [
    path('api/', include('base.api.urls')),
    # path('', views.home, name="home"),
    # path('login', views.login, name="login"),
    # path('logout', views.logout, name="logout"),
    # path('view_email', views.view_email, name="view_email"),
    # path('add_email', views.add_email, name="add_email"),
    # path('add_campaign', views.add_campaign, name="add_campaign"),
    # path('generate-fake-email', views.generate_fake_email, name="generate_fake_email"),
]
