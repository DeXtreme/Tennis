from django.contrib import admin

from courts.models import Court,Worker


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    
    list_display = ["name", "location", "open"]
    search_fields = ["name", "location"]

    ordering = ["name"]

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ["name", "email"]
    search_fields = ["name"]