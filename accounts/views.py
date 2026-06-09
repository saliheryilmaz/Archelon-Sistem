from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, ProfileForm, UserCreateForm, UserEditForm
from .models import CustomUser
import datetime as dt


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get('next', 'dashboard:index'))
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profiliniz güncellendi.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def user_list(request):
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')
    users = CustomUser.objects.exclude(pk=request.user.pk).order_by('role', 'first_name', 'last_name')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def user_create(request):
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Kullanıcı oluşturuldu.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Yeni Kullanıcı'})


@login_required
def user_delete(request, pk):
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        messages.error(request, 'Kendinizi silemezsiniz.')
        return redirect('accounts:user_list')
    if request.method == 'POST':
        name = user.get_full_name() or user.username
        user.delete()
        messages.success(request, f'{name} silindi.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'del_user': user})


@login_required
def user_edit(request, pk):
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')
    user = get_object_or_404(CustomUser, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Kullanıcı güncellendi.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Kullanıcı Düzenle', 'edit_user': user})


@login_required
def user_report(request, pk):
    """Üye karnesi: hangi günler geldi, hangi ders, hangi eğitmen."""
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')

    from appointments.models import Appointment
    from django.db.models import Q

    member = get_object_or_404(CustomUser, pk=pk)

    # Tüm iptal edilmemiş randevular (onaylı + tamamlanmış)
    appointments = (
        Appointment.objects
        .filter(
            user=member,
            status__in=[Appointment.STATUS_CONFIRMED, Appointment.STATUS_COMPLETED]
        )
        .select_related('instructor', 'user_package__package_type')
        .order_by('date', 'start_time')
    )

    OZEL_SLUG = 'ozel_ders'

    total_sessions = appointments.count()
    attended_sessions = appointments.filter(attended=True).count()
    missed_sessions = appointments.filter(attended=False).count()
    group_count = appointments.filter(~Q(user_package__package_type__slug=OZEL_SLUG)).count()
    private_count = appointments.filter(user_package__package_type__slug=OZEL_SLUG).count()

    # Günlük gruplama
    days = {}
    for appt in appointments:
        day = appt.date
        if day not in days:
            days[day] = []
        start_dt = dt.datetime.combine(appt.date, appt.start_time)
        end_dt = dt.datetime.combine(appt.date, appt.end_time)
        duration = (end_dt - start_dt).seconds // 60
        days[day].append({
            'appt': appt,
            'is_private': appt.user_package.package_type.slug == OZEL_SLUG,
            'duration_min': duration,
        })

    day_list = [
        {'date': d, 'sessions': s, 'count': len(s)}
        for d, s in sorted(days.items())
    ]

    # Aktif paketler
    from packages.models import UserPackage
    active_packages = UserPackage.objects.filter(
        user=member, is_active=True
    ).select_related('package_type').order_by('-assigned_at')

    return render(request, 'accounts/user_report.html', {
        'member': member,
        'day_list': day_list,
        'total_sessions': total_sessions,
        'attended_sessions': attended_sessions,
        'missed_sessions': missed_sessions,
        'group_count': group_count,
        'private_count': private_count,
        'unique_days': len(day_list),
        'active_packages': active_packages,
    })
