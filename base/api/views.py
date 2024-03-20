from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import *
# Create your views here.
from base.api.serializers import *

@api_view(['GET', 'POST'])
def add_user_email(request):
    if request.method == "POST":
        email_host_user = request.data['email_host_user']
        email_host_password = request.data['email_host_password']
        email_host_port = request.data['email_host_port']
        email_host_smtp_host = request.data['email_host_smtp_host']
        email_host_use_tls = True if request.data['email_host_use_tls'] == "on" else False
        daily_sending_limit = request.data['daily_sending_limit']
        user_id = request.data['user_id']
        try:
            Email.objects.get(email_host_user = email_host_user)
            return Response({"status": 304, "detail":"Email Already Exist"})
        except:
            new_email = Email.objects.create(
                user_id = user_id,
                email_host_user = email_host_user,
                email_host_password = email_host_password,
                email_host_port = email_host_port,
                email_host_smtp_host = email_host_smtp_host,
                email_host_use_tls = email_host_use_tls,
                daily_sending_limit=daily_sending_limit,
            )
            
            return Response({"status": 201, "detail":"Email Successfully linked with your account. We are validating your email to check if it allow us to send email. You can see the status of your email in Emails tab."})


    return Response({"status": 405})

@api_view(['GET'])
def get_user_emails(request, user_id, condition):
    all_linked_emails = None
    if condition=="good":
        all_linked_emails = Email.objects.filter(user_id=user_id, verified=True)
    else:
        all_linked_emails = Email.objects.filter(user_id=user_id, verified=False)

    emails = EmailSerializer(all_linked_emails, many=True)
    status = 204 if not (emails.data) else 200
    return Response({"emails":emails.data, "status": status })