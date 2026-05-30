from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from appointments.models import Appointment
from packages.models import UserPackage
from accounts.models import CustomUser


@login_required
def index(request):
    today = timezone.now().date()
    user = request.user

    if user.is_admin_role:
        upcoming = Appointment.objects.filter(
            date__gte=today
        ).exclude(status=Appointment.STATUS_CANCELLED).select_related(
            'user', 'instructor', 'user_package__package_type'
        ).order_by('date', 'start_time')[:10]

        total_members = CustomUser.objects.filter(role='member', is_active=True).count()
        today_appts = Appointment.objects.filter(date=today).exclude(status=Appointment.STATUS_CANCELLED).count()
        expired_packages = UserPackage.objects.filter(
            is_active=True, remaining_sessions=0
        ).count()
        pending_appts = Appointment.objects.filter(status=Appointment.STATUS_PENDING).count()

        context = {
            'upcoming': upcoming,
            'total_members': total_members,
            'today_appts': today_appts,
            'expired_packages': expired_packages,
            'pending_appts': pending_appts,
            'is_admin': True,
        }
    else:
        active_packages = user.packages.filter(is_active=True).select_related('package_type')
        upcoming = user.appointments.filter(
            date__gte=today
        ).exclude(status=Appointment.STATUS_CANCELLED).select_related(
            'instructor', 'user_package__package_type'
        ).order_by('date', 'start_time')[:5]

        low_sessions = active_packages.filter(remaining_sessions__lte=2, remaining_sessions__gt=0)

        context = {
            'active_packages': active_packages,
            'upcoming': upcoming,
            'low_sessions': low_sessions,
            'is_admin': False,
        }

    return render(request, 'dashboard/index.html', context)
