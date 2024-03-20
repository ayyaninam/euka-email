from django.db import models
from django_celery_beat.models import PeriodicTask

# Create your models here.

CAMPAIGN_STATUS_CHOICES = [
    ('Stop', 'Stop'),
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
]

class Email(models.Model):
    user_id = models.CharField(max_length=255, null=True, blank=True)
    email_host_user = models.CharField(max_length=255, null=False, blank=False)
    email_host_password = models.CharField(max_length=255, null=False, blank=False)
    email_host_port = models.SmallIntegerField(null=False, blank=False, default=587)
    email_host_smtp_host = models.CharField(max_length=255, null=False, blank=False)
    email_host_use_tls = models.BooleanField(null=False, blank=False, default=True)
    daily_sending_limit = models.SmallIntegerField(null=False, blank=False, default=20)
    today_email_sent = models.SmallIntegerField(null=False, blank=False, default=0)
    verified = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self) -> str:
        return self.email_host_user
    
class TestEmail(models.Model):
    email = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self) -> str:
        return self.email

class Campaign(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=255, null=False, blank=False)
    base_time_gap = models.SmallIntegerField(null=True, blank=True, default=1)
    random_time_gap = models.SmallIntegerField(null=True, blank=True, default=1)
    from_emails = models.ManyToManyField(Email)
    to_emails = models.ManyToManyField(TestEmail)
    subject = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=CAMPAIGN_STATUS_CHOICES, default='Stop')

    def __str__(self) -> str:
        return self.name

class ScheduledEmail(models.Model):
    from_email = models.ForeignKey(Email, on_delete=models.CASCADE, null=False)
    to_email = models.CharField(max_length=255, null=False, blank=False)
    attached_campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True, blank=True)
    task_attached = models.ForeignKey(PeriodicTask, on_delete=models.CASCADE, null=True)
    sent = models.BooleanField(default=False, null=False, blank=False)
    final_result = models.CharField(max_length=255, null=False, blank=False, default="Processing!")

    def __str__(self) -> str:
        return f"{self.from_email} → {self.to_email}"

