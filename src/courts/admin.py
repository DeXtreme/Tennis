from django.contrib import admin

from .models import Court,Worker


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    pass

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    pass