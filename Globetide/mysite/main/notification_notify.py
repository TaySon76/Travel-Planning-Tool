from django.contrib.auth.models import User
from .models import Notification

def new_notification(user):
    if user.is_anonymous:
        return False
    else:
        return bool(Notification.objects.filter(user=user, unread=True))