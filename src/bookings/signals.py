from datetime import timedelta,datetime
from django.db.models.signals import post_save,post_delete,pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


from . import models,tasks,serializers


@receiver(pre_save, sender=models.Booking)
def send_messages_before_save(sender, instance, **kwargs):
    new_booking = instance

    try:
        old_booking = models.Booking.objects.get(booking_id=new_booking.booking_id)
        
        channel_layer = get_channel_layer()

        serializer = serializers.CancelledSerializer(old_booking)
        sub = f"court_{old_booking.court.court_id}"

        details = {"cancelled": serializer.data}
        async_to_sync(channel_layer.group_send)(
            sub, {
                "type": "event",
                "body": details
            }
        )
        
    except models.Booking.DoesNotExist:
        pass



@receiver(post_save, sender=models.Booking)
def send_messages_on_save(sender, instance, created, **kwargs):

    booking = instance
    
    if created: 
        tasks.send_confirmation.apply_async(args=(
            booking.account.user.username,
            booking.court.name,
            booking.start_time,
            booking.duration
        ))

        tasks.send_reminders.apply_async(args=(
            booking.account.user.username,
            booking.court.name,
            booking.start_time,
            booking.duration
        ), eta=booking.start_time - timedelta(hours=12))

        
        tasks.send_admin_notification.apply_async(args=[str(booking)])
   
    else:
        tasks.send_booking_change.apply_async(args=(
            booking.account.user.username,
            booking.court.name,
            booking.start_time,
            booking.duration
        ))

    tasks.send_worker_reminders.apply_async(
        args=(str(booking.court.court_id),booking.court.name),
        eta=datetime.now()+timedelta(minutes=2)
    )

    channel_layer = get_channel_layer()
    
    serializer = serializers.BookedSerializer(booking)
    sub = f"court_{booking.court.court_id}"

    details = {"booked": serializer.data}
    async_to_sync(channel_layer.group_send)(
        sub, {
            "type": "event",
            "body": details
        }
    )
        

@receiver(post_delete, sender=models.Booking)
def send_messages_on_delete(sender, instance, **kwargs):

    booking = instance
    
    tasks.send_cancellation.apply_async(args=(
            booking.account.user.username,
            booking.court.name,
            booking.start_time,
            booking.duration
    ))
    

    tasks.send_cancel_admin_notification.apply_async(args=[str(booking)])

    channel_layer = get_channel_layer()

    serializer = serializers.CancelledSerializer(booking)
    sub = f"court_{booking.court.court_id}"

    details = {"cancelled": serializer.data}
    async_to_sync(channel_layer.group_send)(
        sub, {
            "type": "event",
            "body": details
        }
    )