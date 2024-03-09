from django.contrib import admin

from .models import Booking,Court

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    pass

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    pass
