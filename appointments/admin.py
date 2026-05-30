from django.contrib import admin
from .models import Appointment, Instructor


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time', 'instructor', 'status', 'user_package')
    list_filter = ('status', 'date', 'instructor')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_editable = ('status',)
    date_hierarchy = 'date'
