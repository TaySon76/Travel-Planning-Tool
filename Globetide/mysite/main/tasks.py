from django_cron import CronJobBase, Schedule
from django.utils import timezone
from .models import UserProfile, UserActivity
from celery import shared_task

class ResetExpiredCodesJob(CronJobBase):
    schedule = Schedule(run_every_mins=30) 
    code = 'main.reset_expired_codes_job'  

    def do(self):
        UserProfile.objects.filter(
            code_expiry_time__lt=timezone.now(),
            otp__isnull=False
        ).update(otp='', otp_expiry_time=None)


@shared_task
def clear_login_dates():
    UserActivity.objects.update(login_dates={})

    