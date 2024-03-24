from django.contrib import admin
from django.urls import path
from . import views

app_name = "base"

urlpatterns = [
    path('stats/<str:user_id>', views.stats, name="stats"),
    path('add-user-email', views.add_user_email, name="add_user_email"),
    path('get-user-emails/<str:user_id>/<str:condition>', views.get_user_emails, name="get_user_emails"),
    
    path('delete-user-email/<str:user_id>/<int:email_id>', views.delete_user_email, name="delete_user_email"),
    path('get-all-campaigns/<str:user_id>', views.get_all_campaigns, name="get_all_campaigns"),
    path('create-new-campaign/<str:user_id>', views.create_new_campaign, name="create_new_campaign"),
    path('delete-campaign/<str:user_id>/<int:campaign_id>', views.delete_campaign, name="delete_campaign"),
    path('run-campaign/<str:user_id>/<int:campaign_id>/<str:action>', views.run_campaign, name="run_campaign"),
    path('campaign-details/<str:user_id>/<int:campaign_id>', views.campaign_details, name="campaign_details"),
    path('campaign-activity/<int:campaign_id>', views.campaign_activity, name="campaign_activity"),

]
