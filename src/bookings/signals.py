from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

from . import models

@receiver(post_save, sender=models.Booking)
def send_email_on_save(sender, instance, created, **kwargs):

    booking = instance
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [booking.account.user.username] 
    if created: 
        subject = 'Booking Confirmation'
        message = f"You have booked {booking.court.name} from {booking.start_time} for {booking.duration} hours"
        
        admins = User.objects.filter(is_superuser=True,email__isnull=False)
        admin_email_list = [admin.email for admin in admins]

        subject = 'New Booking'
        message = f"Account:{booking.account} Booking:{booking}"
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(subject, message, from_email, admin_email_list)
    else:
        subject = 'Booking Modification'
        message = f"Your booking has been changed to {booking.court.name} from {booking.start_time} for {booking.duration} hours"
    
    send_mail(subject, message, from_email, recipient_list)


@receiver(post_delete, sender=models.Booking)
def send_email_on_delete(sender, instance, **kwargs):

    booking = instance
    from_email = settings.DEFAULT_FROM_EMAIL

    subject = 'Booking Cancellation'
    message = f"You have cancelled your booking for {booking.court.name} from {booking.start_time} for {booking.duration} hours"
    recipient_list = [booking.account.user.username] 

    send_mail(subject, message, from_email, recipient_list)

    admins = User.objects.filter(is_superuser=True,email__isnull=False)
    admin_email_list = [admin.email for admin in admins]
    subject = 'New Cancellation'
    message = f"Booking:{booking}"

    send_mail(subject, message, from_email, admin_email_list)
