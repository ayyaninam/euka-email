from rest_framework import serializers
from base.models import *
from django_celery_beat.models import ClockedSchedule, PeriodicTask


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = [
            "id",
            "email_host_user",
            "daily_sending_limit",
            "today_email_sent",
            "verified",
        ]


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "name",
            "base_time_gap",
            "random_time_gap",
            "today_email_sent",
            "total_email_sent",
            "status",
            "from_emails",
            "to_emails",
            "subject",
            "body",
        ]
        # depth = 1


class AllCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "id",
            "created_at",
            "name",
            "status",
            "from_emails",
            "to_emails",
            "today_email_sent",
            "total_email_sent",
            "subject",
            "body",
        ]


class ClockedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClockedSchedule
        fields = ["clocked_time"]


class TaskAttachedSerializer(serializers.ModelSerializer):
    clocked = ClockedSerializer()

    class Meta:
        model = PeriodicTask
        fields = ["clocked"]


class ScheduledEmailSerializer(serializers.ModelSerializer):
    task_attached = TaskAttachedSerializer()
    from_email = EmailSerializer()

    class Meta:
        model = ScheduledEmail
        fields = [
            "from_email",
            "to_email",
            "task_attached",
            "sent",
            "final_result",
        ]
