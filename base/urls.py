from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "base"

urlpatterns = [
    path("api/", include("base.api.urls")),
]
