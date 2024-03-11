from datetime import timedelta
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from celery import shared_task

from courts.models import Worker
from . import models

@shared_task
def send_reminders():
    
    now = timezone.now() 
    last_created_at = cache.get("send_reminder_last_created_at", now-timedelta(days=10))

    tomorrow = now + timedelta(days=1)
    bookings = models.Booking.objects.filter(start_time__date=tomorrow.date(),
                                             created_at__gt=last_created_at).order_by("created_at")

    from_email = settings.DEFAULT_FROM_EMAIL
    for booking in bookings:
        recipient_list = [booking.account.user.username] 

        subject = 'Booking Reminder'
        message = f"You have booked {booking.court.name} from {booking.start_time} for {booking.duration} hours"
    
        send_mail(subject, message, from_email, recipient_list)

        last_created_at = booking.created_at
    
    cache.set("send_reminder_last_created_at", last_created_at, None)


@shared_task
def send_worker_reminders():
    now = timezone.now() 
    start = now - timedelta(minutes=20)
    completed_bookings = models.Booking.objects.filter(end_time__gte=start,end_time__lte=now)

    from_email = settings.DEFAULT_FROM_EMAIL
    for booking in completed_bookings:
        workers = Worker.objects.filter(court=booking.court)
        recipient_list = [worker.email for worker in workers] 

        subject = 'Cleaning Reminder'
        message = f"You are reminded to clean {booking.court.name} for 10 minutes"
    
        send_mail(subject, message, from_email, recipient_list)