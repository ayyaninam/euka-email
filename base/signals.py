from .tasks import send_test_email_adding_models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from base.models import *
import datetime
from base.tasks import schedule_email_under_celery, delete_scheduled_cluster



@receiver(post_save, sender=Email)
def working_email_checker(sender, instance, **kwargs):
    if not instance.verified:
        send_test_email_adding_models(
            instance.id,
            instance.email_host_user,
            instance.email_host_password,
            instance.email_host_use_tls,
            instance.email_host_smtp_host,
            instance.email_host_port,
        )


@receiver(pre_save, sender=Campaign)
def campaign_active_email_scheduler(sender, instance, **kwargs):
    old_status = None
    new_status = instance.status
    try:
        old_status = Campaign.objects.get(id=instance.id).status
    except:
        old_status = 'New'
        instance.status = 'Stop'

    if old_status != 'New':
        if ((old_status == "In Progress") and (new_status == "Stop")):
            # deleting the cluster; and scheduled emails 
            # if someone stop the campaign in middle.
            delete_scheduled_cluster.delay(campaign_id=instance.id)

        elif ((old_status == "Stop") and (new_status == "In Progress")):

            schedule_email_under_celery.delay(campaign_id=instance.id)