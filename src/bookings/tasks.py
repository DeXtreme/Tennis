from django.contrib.auth.models import User
from django.conf import settings
from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task

from courts.models import Worker


@shared_task
def send_confirmation(email,court_name,start_time,duration):
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email] 

    subject = 'Booking Confirmation'
    message = f"You have booked {court_name} from {start_time} for {duration} hours"

    send_mail(subject, message, from_email, recipient_list)



@shared_task
def send_reminders(email,court_name,start_time,duration):
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email] 

    subject = 'Booking Reminder'
    message = f"You have booked {court_name} from {start_time} for {duration} hours"

    send_mail(subject, message, from_email, recipient_list)

@shared_task
def send_booking_change(email,court_name,start_time,duration):
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email] 

    subject = 'Booking Modification'
    message = f"Your booking has been changed to {court_name} from {start_time} for {duration} hours"

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_admin_notification(booking_info):

    recipient_list = User.objects.filter(is_superuser=True,email__isnull=False).values_list("email")
    from_email = settings.DEFAULT_FROM_EMAIL

    subject = 'New Booking Notification'
    message = f"{booking_info}"

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_cancellation(email,court_name,start_time,duration):
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email] 

    subject = 'Booking Cancellation'
    message = f"You have cancelled your booking for {court_name} from {start_time} for {duration} hours"

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_cancel_admin_notification(booking_info):

    recipient_list = User.objects.filter(is_superuser=True,email__isnull=False).values_list("email")
    from_email = settings.DEFAULT_FROM_EMAIL

    subject = 'Booking Cancelled Notification'
    message = f"{booking_info}"

    send_mail(subject, message, from_email, recipient_list)

@shared_task
def send_worker_reminders(court_id, court_name):

    recipient_list = Worker.objects.filter(court__court_id=court_id).values_list("email")
    from_email = settings.DEFAULT_FROM_EMAIL

    subject = 'Cleaning Reminder'
    message = f"You are reminded to clean {court_name} for 10 minutes"

    
    send_mail(subject, message, from_email, recipient_list)
    
