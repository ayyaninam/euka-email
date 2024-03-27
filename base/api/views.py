from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import *
# Create your views here.
from base.api.serializers import *
from django.db.models import Sum


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
    return Response({"data":emails.data, "status": status })


@api_view(['GET'])
def delete_user_email(request, user_id, email_id):
    deletable_emails = Email.objects.filter(user_id=user_id, id=email_id)
    status = 400 if not (deletable_emails) else 200

    if deletable_emails:
        deletable_emails.delete()
    
    return Response({"status": status })


@api_view(['GET'])
def get_all_campaigns(request, user_id):
    all_campaigns = Campaign.objects.filter(user_id=user_id).order_by('-created_at')

    campaigns = AllCampaignSerializer(all_campaigns, many=True)
    status = 204 if not (campaigns.data) else 200

    return Response({"data":campaigns.data, "status": status })


@api_view(['POST'])
def create_new_campaign(request, user_id):
    if request.method == "POST":
        user_id = request.data['user_id']
        name = request.data['name']
        base_time_gap = request.data['base_time_gap']
        random_time_gap = request.data['random_time_gap']
        from_emails_ids = request.data['from_emails']
        to_emails = request.data['to_emails']
        subject = request.data['subject']
        body = request.data['body']

        if not user_id or not name or not base_time_gap or not random_time_gap or not from_emails_ids or not to_emails or not subject or not body:

            return Response({"status": 400, "details":"Missing required fields."})

        try:
            from_emails_ids = [int(x) for x in from_emails_ids]
        except ValueError:
            return Response({"status": 400, "details": "Invalid format for 'from_emails'."})


        if not from_emails_ids:
            return Response({"status": 400, "details":"Select atleast one Email."})

        from_emails_ids = [int(x) for x in from_emails_ids]
        created_campaign = Campaign.objects.create(
            user_id = user_id,
            name = name,
            base_time_gap = base_time_gap,
            random_time_gap = random_time_gap,
            subject = subject,
            body = body,
        )

        to_emails_ids = []
        for email in to_emails:
            to_email_obj, _ = SendToEmail.objects.get_or_create(email=email)
            to_emails_ids.append(to_email_obj.id)


        created_campaign.from_emails.add(*from_emails_ids)
        created_campaign.to_emails.add(*to_emails_ids)

        return Response({"status": 201})

@api_view(['GET'])
def delete_campaign(request, user_id, campaign_id):
    deletable_campaigns = Campaign.objects.filter(user_id=user_id, id=campaign_id)
    status = 400 if not (deletable_campaigns) else 200
    
    if deletable_campaigns:
        deletable_campaigns.delete()


    return Response({"status": status })
    


@api_view(['GET'])
def run_campaign(request, user_id, campaign_id, action):
    status = None
    
    try:
        runable_campaign = Campaign.objects.filter(user_id=user_id, id=campaign_id)
        if runable_campaign:
            runable_campaign = runable_campaign.first()
            runable_campaign.status = "In Progress" if action == "start" else "Stop"
            runable_campaign.save()
            status = 200
    except:
        status = 400
    
    return Response({"status": status })

    



@api_view(['GET'])
def campaign_details(request, user_id, campaign_id):
    campaign = Campaign.objects.filter(user_id=user_id, id=campaign_id)
    resp = None
    if campaign:
        campaign = campaign.first()
        resp = CampaignSerializer(campaign, many=False)

    status = 400 if not (campaign) else 200

    return Response({"data":resp.data, "status": status })

@api_view(['GET'])
def campaign_activity(request, campaign_id):
    campaign = Campaign.objects.filter(id=campaign_id)
    resp = None

    if campaign:
        campaign = campaign.first()
        scheduledEmail = ScheduledEmail.objects.filter(attached_campaign=campaign)

        resp = ScheduledEmailSerializer(scheduledEmail, many=True)

    status = 400 if not (resp.data) else 200

    return Response({"data":resp.data, "status": status })
    

@api_view(['GET'])
def stats(request, user_id):
    campaign = Campaign.objects.filter(user_id=user_id)
    if campaign:
        today_email_sent = campaign.aggregate(Sum('today_email_sent'))
        total_email_sent = campaign.aggregate(Sum('total_email_sent'))
        today_email_sent = today_email_sent if today_email_sent else 0
        total_email_sent = total_email_sent if total_email_sent else 0
    
    status = 400 if not (campaign) else 200

    return Response({
        "today_email_sent":today_email_sent,
        "total_email_sent":total_email_sent,
        "status": status
            })
    

@api_view(['GET'])
def edit_daily_sending_limit(request, email_id, daily_sending_limit):
    email = Email.objects.filter(id=email_id)
    status = 404
    if email:
        email = email.first()
        email.update(daily_sending_limit=daily_sending_limit)
        status = 200

    return Response({"status": status })