from celery import shared_task
from django.core.mail import send_mail, get_connection
from django.conf import settings
from .models import *
from celery.exceptions import Ignore
from base.email_sender import (
    generate_random_time_interval,
    schedule_email_creator_in_db,
)
import traceback
import datetime
from django_celery_beat.models import ClockedSchedule, PeriodicTask
import json
from django.utils.timezone import get_current_timezone


def send_email(from_email, to_email, campaign_id, time_to_send):
    campaign = None
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except:
        pass

    if (campaign) and (campaign.status == "In Progress"):
        if int(from_email.today_email_sent) < int(from_email.daily_sending_limit):
            try:
                connection = get_connection(
                    username=from_email.email_host_user,
                    password=from_email.email_host_password,
                    fail_silently=False,
                    use_tls=from_email.email_host_use_tls,
                    host=from_email.email_host_smtp_host,
                    port=from_email.email_host_port,
                )

                send_mail(
                    subject=f"{campaign.subject}",
                    message=f"{campaign.body}",
                    from_email=from_email.email_host_user,
                    fail_silently=False,
                    recipient_list=[to_email],
                    connection=connection,
                    html_message=None,
                )

                mark_email_as_sent(
                    from_email, to_email, campaign_id, sent=True, final_result="Sent!"
                )

                return True
            except:
                mark_email_as_sent(
                    from_email,
                    to_email,
                    campaign_id,
                    sent=False,
                    final_result="Bounce!",
                )
                return False
        else:
            save_periodic_function(
                from_email,
                to_email,
                campaign,
                time_to_send=time_to_send + datetime.timedelta(days=1),
                reschedule=True,
            )
            mark_email_as_sent(
                from_email,
                to_email,
                campaign_id,
                sent=False,
                final_result="Processing!",
            )
            return False
    else:
        if campaign:
            mark_email_as_sent(
                from_email, to_email, campaign_id, sent=False, final_result="Dead!"
            )

        return False


@shared_task
def send_test_email_adding_models(
    email_id,
    email_host_user,
    email_host_password,
    email_host_use_tls,
    email_host_smtp_host,
    email_host_port,
):
    try:
        connection = get_connection(
            username=email_host_user,
            password=email_host_password,
            fail_silently=False,
            use_tls=email_host_use_tls,
            host=email_host_smtp_host,
            port=email_host_port,
        )

        send_mail(
            subject=f"Email Integration with {settings.SITE_NAME}",
            message=f"This Email is now connected with {settings.SITE_NAME}. {email_host_user}",
            from_email=email_host_user,
            # auth_user = config.email_host_user,
            # auth_password = config.email_host_password,
            fail_silently=False,
            recipient_list=[settings.EMAIL_RECEIVER_AS_A_CHECKER],
            connection=connection,
            html_message=None,
        )

        Email.objects.filter(id=email_id).update(verified=True)
        return "Success!"
    except Exception as e:
        Email.objects.filter(id=email_id).update(verified=False)
        print("Sending Test Email Failed! Error: ", e)
        traceback.print_exc()
        return "Failed!"


def save_periodic_function(
    from_email, to_email, campaign, time_to_send, reschedule=False
):

    clockedsch, clockedsch_created = ClockedSchedule.objects.get_or_create(
        clocked_time=time_to_send
    )
    periodic_task = None
    if reschedule:
        try:
            periodic_task = PeriodicTask.objects.get(
                name=f"C: {campaign.id} - F:{from_email} - T:{to_email}"
            )
            periodic_task.args = json.dumps(
                [
                    from_email.id,
                    to_email,
                    campaign.id,
                    time_to_send.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )
            periodic_task.save()
        except:
            pass
    else:
        try:
            periodic_task = PeriodicTask.objects.create(
                clocked=clockedsch,
                name=f"C: {campaign.id} - F:{from_email} - T:{to_email}",
                task="base.tasks.send_email_under_beat",
                args=json.dumps(
                    [
                        from_email.id,
                        to_email,
                        campaign.id,
                        time_to_send.strftime("%Y-%m-%d %H:%M:%S"),
                    ]
                ),
                one_off=True,
            )
        except:
            pass

    if periodic_task:
        ScheduledEmail.objects.create(
            from_email=from_email,
            to_email=to_email,
            attached_campaign=campaign,
            task_attached=periodic_task,
        )

    return None


@shared_task
def delete_scheduled_cluster(campaign_id):

    campaign = None
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except:
        pass
    if campaign:
        emails_to_delete = ScheduledEmail.objects.filter(
            attached_campaign=campaign, sent=False
        )

        # Loop through each email and delete associated task_attached and clocked entries
        for email in emails_to_delete:
            if email.task_attached:
                # Delete associated clocked entry
                email.task_attached.clocked.delete()
                # Delete task_attached entry
                email.task_attached.delete()

        emails_to_delete.delete()

    return None


@shared_task
def schedule_email_under_celery(campaign_id):

    campaign = None
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except:
        pass

    if campaign:
        base_time_gap_in_sec = int(campaign.base_time_gap) * 60
        random_time_gap_in_sec = int(campaign.random_time_gap) * 60
        # base_time_gap_in_sec = 1
        # random_time_gap_in_sec = 1

        today_time = datetime.datetime.now(tz=get_current_timezone())
        # today_time = datetime.datetime.now(tz=get_current_timezone()) + datetime.timedelta(minutes=5)

        to_emails = list(
            set(list(campaign.to_emails.all().values_list("email", flat=True)))
        )
        from_emails = Campaign.objects.get(id=campaign_id).from_emails.all()

        for from_email in from_emails:

            today_email_sent_value = int(from_email.today_email_sent)

            time_to_send = (
                today_time
                + datetime.timedelta(seconds=base_time_gap_in_sec)
                + generate_random_time_interval(random_time_gap_in_sec)
            )

            while (today_email_sent_value < from_email.daily_sending_limit) and (
                to_emails
            ):

                save_periodic_function(
                    from_email=from_email,
                    to_email=to_emails[0],
                    campaign=campaign,
                    time_to_send=time_to_send,
                )

                to_emails.pop(0)

                time_to_send = (
                    time_to_send
                    + datetime.timedelta(seconds=base_time_gap_in_sec)
                    + generate_random_time_interval(random_time_gap_in_sec)
                )

                today_email_sent_value += 1

        while to_emails:
            today_time = today_time + datetime.timedelta(days=1)
            time_to_send = (
                today_time
                + datetime.timedelta(seconds=base_time_gap_in_sec)
                + generate_random_time_interval(random_time_gap_in_sec)
            )

            for from_email in from_emails:

                next_day_volumn = 0

                while (next_day_volumn < from_email.daily_sending_limit) and (
                    to_emails
                ):

                    save_periodic_function(
                        from_email=from_email,
                        to_email=to_emails[0],
                        campaign=campaign,
                        time_to_send=time_to_send,
                    )

                    time_to_send = (
                        time_to_send
                        + datetime.timedelta(seconds=base_time_gap_in_sec)
                        + generate_random_time_interval(random_time_gap_in_sec)
                    )

                    to_emails.pop(0)

                    next_day_volumn += 1

        return to_emails


def mark_email_as_sent(from_email, to_email, campaign_id, sent=True, final_result=None):
    campaign = Campaign.objects.get(id=campaign_id)

    scheduled_email = ScheduledEmail.objects.filter(
        from_email=from_email,
        to_email=to_email,
        attached_campaign=campaign,
    )

    if scheduled_email:
        scheduled_email.update(sent=sent)

    from_email.today_email_sent = int(from_email.today_email_sent) + 1
    from_email.save()

    if final_result:
        scheduled_email.update(final_result=final_result)

    campaign.today_email_sent = campaign.today_email_sent + 1
    campaign.total_email_sent = campaign.total_email_sent + 1
    campaign.save()


@shared_task
def send_email_under_beat(from_email_id, to_email, campaign_id, time_to_send=None):
    from_email = None
    try:
        from_email = Email.objects.get(id=from_email_id)
    except:
        pass

    if time_to_send:
        time_to_send = datetime.datetime.strptime(time_to_send, "%Y-%m-%d %H:%M:%S")

    if from_email:
        send_email(from_email, to_email, campaign_id, time_to_send)

        return f"Email Sent!"


@shared_task
def make_email_at_zero():
    all_emails = Email.objects.all().update(today_email_sent=0)
    all_emails = Campaign.objects.all().update(today_email_sent=0)
    return True
