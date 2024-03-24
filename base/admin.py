from django.contrib import admin
from .models import *
# Register your models here.
class EmailAdmin(admin.ModelAdmin):
    list_display = ["email_host_user","email_host_password","email_host_port","email_host_smtp_host","email_host_use_tls","daily_sending_limit"]
class ScheduledEmailAdmin(admin.ModelAdmin):
    list_display = ['task_attached', 'sent']

admin.site.register(Email, EmailAdmin)
admin.site.register(ScheduledEmail, ScheduledEmailAdmin)
admin.site.register(Campaign)
admin.site.register(SendToEmail)