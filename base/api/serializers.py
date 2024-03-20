from rest_framework import serializers
from base.models import *


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = [
            "email_host_user",
            "daily_sending_limit",
            "today_email_sent",
            "verified"
        ]