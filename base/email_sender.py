from django.core.mail import send_mail, get_connection
from django.conf import settings
from base.models import *
import datetime
import random


def generate_random_time_interval(max_seconds):
    # Convert minutes to seconds
    # Generate a random number of seconds between 0 and max_seconds
    random_seconds = random.randint(0, max_seconds)
    # Convert seconds to a timedelta object
    random_time_interval = datetime.timedelta(seconds=random_seconds)
    return random_time_interval


def send_test_email_adding_models(config):
    connection = get_connection(
        username=config.email_host_user,
        password=config.email_host_password,
        fail_silently=False,
        use_tls=config.email_host_use_tls,
        host=config.email_host_smtp_host,
        port=config.email_host_port,
    )

    send_mail(
        subject=f"Email Integration with {settings.SITE_NAME}",
        message=f"This Email is now connected with {settings.SITE_NAME}. {config.email_host_user}",
        from_email=config.email_host_user,
        fail_silently=False,
        recipient_list=[settings.EMAIL_RECEIVER_AS_A_CHECKER],
        connection=connection,
        html_message=None,
    )


def schedule_email_creator_in_db(
    from_email, to_emails, attached_campaign_id, time_to_send
):
    ScheduledEmail.objects.create(
        from_email=from_email,
        to_email=to_emails,
        attached_campaign=Campaign.objects.get(id=attached_campaign_id),
        time_to_send=time_to_send,
    )
