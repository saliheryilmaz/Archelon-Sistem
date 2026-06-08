from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from .models import Appointment, Instructor
from .forms import AppointmentForm, AdminAppointmentForm, InstructorAssignForm, InstructorForm


@login_required
def appointment_list(request):
    if request.user.is_admin_role:
        appointments = Appointment.objects.select_related(
            'user', 'user_package__package_type', 'instructor'
        ).order_by('-date', '-start_time')
        can_request = False
    else:
        appointments = request.user.appointments.select_related(
            'user_package__package_type', 'instructor'
        ).order_by('-date', '-start_time')
        from packages.models import UserPackage
        can_request = UserPackage.objects.filter(
            user=request.user,
            is_active=True,
            remaining_sessions__gt=0,
            package_type__slug='ozel_ders'
        ).exists()
    return render(request, 'appointments/list.html', {
        'appointments': appointments,
        'can_request': can_request,
    })


@login_required
def create_appointment(request):
    from packages.models import UserPackage

    # ── Admin akışı ──────────────────────────────────────────────
    if request.user.is_admin_role:
        form = AdminAppointmentForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            member = form.cleaned_data['member']
            # Formdan seçilen paketi al, yoksa en son aktif paketi kullan
            from packages.models import UserPackage
            selected_pkg_id = request.POST.get('selected_package')
            if selected_pkg_id:
                pkg = UserPackage.objects.filter(
                    pk=selected_pkg_id, user=member, is_active=True, remaining_sessions__gt=0
                ).select_related('package_type').first()
            else:
                pkg = UserPackage.objects.filter(
                    user=member, is_active=True, remaining_sessions__gt=0
                ).select_related('package_type').order_by('-assigned_at').first()

            if not pkg:
                messages.error(request, f'{member} adlı üyenin aktif paketi bulunmuyor.')
            else:
                try:
                    appt = form.save(commit=False)
                    appt.user = member
                    appt.user_package = pkg
                    appt.status = Appointment.STATUS_CONFIRMED
                    appt.save()
                    pkg.use_session()
                    messages.success(
                        request,
                        f'{member} için randevu oluşturuldu ve onaylandı. '
                        f'Kalan seans: {pkg.remaining_sessions}'
                    )
                    return redirect('appointments:list')
                except ValidationError as e:
                    messages.error(request, str(e.message))

        return render(request, 'appointments/admin_create.html', {'form': form})

    # ── Üye akışı ────────────────────────────────────────────────
    active_packages = UserPackage.objects.filter(
        user=request.user,
        is_active=True,
        remaining_sessions__gt=0,
        package_type__slug='ozel_ders'
    )
    if not active_packages.exists():
        messages.warning(request, 'Randevu talebi yalnızca Özel Ders paketi sahiplerine açıktır.')
        return redirect('appointments:list')

    form = AppointmentForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            appt = form.save(commit=False)
            appt.user = request.user
            appt.save()
            messages.success(request, 'Randevu talebiniz alındı. Admin onayladıktan sonra seans hakkınız düşecektir.')
            return redirect('appointments:list')
        except ValidationError as e:
            messages.error(request, str(e.message))
    return render(request, 'appointments/create.html', {'form': form})


@login_required
def cancel_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if appt.user != request.user and not request.user.is_admin_role:
        messages.error(request, 'Bu randevuyu iptal etme yetkiniz yok.')
        return redirect('appointments:list')
    if request.method == 'POST':
        appt.cancel()
        messages.success(request, 'Randevu iptal edildi.')
        return redirect('appointments:list')
    return render(request, 'appointments/confirm_cancel.html', {'appt': appt})


@login_required
def confirm_appointment(request, pk):
    if not request.user.is_admin_role:
        messages.error(request, 'Bu işlem için yetkiniz yok.')
        return redirect('appointments:list')
    appt = get_object_or_404(Appointment, pk=pk)
    if appt.status != Appointment.STATUS_PENDING:
        messages.warning(request, 'Bu randevu zaten işleme alınmış.')
        return redirect('appointments:list')
    form = InstructorAssignForm(request.POST or None, instance=appt)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save(commit=False)
            appt.instructor = form.cleaned_data.get('instructor')
            appt.confirm()
            messages.success(request, f'Randevu onaylandı. Üyenin kalan seans hakkı: {appt.user_package.remaining_sessions}')
            return redirect('appointments:list')
        except ValidationError as e:
            messages.error(request, str(e.message))
    return render(request, 'appointments/confirm_appointment.html', {'appt': appt, 'form': form})


@login_required
def instructor_list(request):
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')
    instructors = Instructor.objects.all()
    return render(request, 'appointments/instructor_list.html', {'instructors': instructors})


@login_required
def instructor_create(request):
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')
    form = InstructorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Eğitmen eklendi.')
        return redirect('appointments:instructor_list')
    return render(request, 'appointments/instructor_form.html', {'form': form, 'title': 'Yeni Eğitmen'})


@login_required
def instructor_edit(request, pk):
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')
    instructor = get_object_or_404(Instructor, pk=pk)
    form = InstructorForm(request.POST or None, instance=instructor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Eğitmen güncellendi.')
        return redirect('appointments:instructor_list')
    return render(request, 'appointments/instructor_form.html', {'form': form, 'title': 'Eğitmen Düzenle'})


@login_required
def instructor_delete(request, pk):
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')
    instructor = get_object_or_404(Instructor, pk=pk)
    if request.method == 'POST':
        name = instructor.name
        instructor.delete()
        messages.success(request, f'{name} silindi.')
        return redirect('appointments:instructor_list')
    return render(request, 'appointments/instructor_confirm_delete.html', {'instructor': instructor})


@login_required
def attendance_sheet(request):
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')

    from datetime import date, time as dt_time
    selected_date_str = request.GET.get('date', '')
    selected_time_str = request.GET.get('time', '')
    selected_date = None
    selected_time = None
    grouped = {}        # {instructor_name: [appointment, ...]}
    available_times = []  # o güne ait benzersiz saatler

    if selected_date_str:
        try:
            selected_date = date.fromisoformat(selected_date_str)
        except ValueError:
            selected_date = None

    if selected_date:
        # O güne ait tüm onaylı randevuların saatlerini çek (dropdown için)
        available_times = list(
            Appointment.objects
            .filter(date=selected_date, status=Appointment.STATUS_CONFIRMED)
            .values_list('start_time', flat=True)
            .distinct()
            .order_by('start_time')
        )

        # Saat filtresi
        if selected_time_str:
            try:
                h, m = selected_time_str.split(':')
                selected_time = dt_time(int(h), int(m))
            except (ValueError, AttributeError):
                selected_time = None

        qs = Appointment.objects.filter(
            date=selected_date, status=Appointment.STATUS_CONFIRMED
        )
        if selected_time:
            qs = qs.filter(start_time=selected_time)

        appointments = qs.select_related(
            'user', 'instructor', 'user_package__package_type'
        ).order_by('start_time', 'instructor__name', 'user__first_name')

        for appt in appointments:
            instructor_name = appt.instructor.name if appt.instructor else 'Eğitmensiz'
            if instructor_name not in grouped:
                grouped[instructor_name] = []
            grouped[instructor_name].append(appt)

    return render(request, 'appointments/attendance_sheet.html', {
        'selected_date': selected_date,
        'selected_date_str': selected_date_str,
        'selected_time': selected_time,
        'selected_time_str': selected_time_str,
        'available_times': available_times,
        'grouped': grouped,
        'today': timezone.now().date(),
    })


@login_required
def save_attendance(request):
    """Yoklama geldi/gelmedi durumunu AJAX ile kaydeder."""
    from django.http import JsonResponse
    import json
    if not request.user.is_admin_role:
        return JsonResponse({'ok': False, 'error': 'Yetkisiz'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST gerekli'}, status=405)
    try:
        body = json.loads(request.body)
        appt_id = int(body.get('id'))
        value = body.get('value')  # True, False veya None
    except (ValueError, TypeError, KeyError):
        return JsonResponse({'ok': False, 'error': 'Geçersiz veri'}, status=400)
    appt = get_object_or_404(Appointment, pk=appt_id)
    appt.attended = value
    appt.save(update_fields=['attended'])
    return JsonResponse({'ok': True, 'id': appt_id, 'attended': appt.attended})


@login_required
def instructor_report(request):
    """Eğitmen bazlı seans raporu: kursiyer / özel ders ayrımı, günlük saat detayı."""
    if not request.user.is_admin_role:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')

    from datetime import date, timedelta
    from django.db.models import Count, Q
    from django.db.models.functions import TruncDate
    import datetime as dt

    # Tarih filtresi
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')
    instructor_id = request.GET.get('instructor', '')

    today = timezone.now().date()
    date_from = None
    date_to = None

    if date_from_str:
        try:
            date_from = date.fromisoformat(date_from_str)
        except ValueError:
            date_from = None
    if date_to_str:
        try:
            date_to = date.fromisoformat(date_to_str)
        except ValueError:
            date_to = None

    instructors = Instructor.objects.all()

    # Temel queryset: iptal edilmemiş randevular
    base_qs = Appointment.objects.filter(
        status__in=[Appointment.STATUS_CONFIRMED, Appointment.STATUS_COMPLETED]
    ).select_related('instructor', 'user', 'user_package__package_type')

    if date_from:
        base_qs = base_qs.filter(date__gte=date_from)
    if date_to:
        base_qs = base_qs.filter(date__lte=date_to)
    if instructor_id:
        base_qs = base_qs.filter(instructor_id=instructor_id)

    # Kursiyer slug'ları (özel ders DEĞİL olanlar)
    OZEL_SLUG = 'ozel_ders'

    # Eğitmen bazlı istatistikler
    instructor_stats = []
    for inst in instructors:
        inst_qs = base_qs.filter(instructor=inst)

        group_qs = inst_qs.filter(~Q(user_package__package_type__slug=OZEL_SLUG))
        private_qs = inst_qs.filter(user_package__package_type__slug=OZEL_SLUG)

        group_count = group_qs.count()
        private_count = private_qs.count()
        total_count = group_count + private_count

        if total_count == 0 and not instructor_id:
            continue  # Hiç seans yoksa listeleme (filtre yokken)

        # Toplam saat hesapla
        total_minutes = 0
        for appt in inst_qs:
            start_dt = dt.datetime.combine(appt.date, appt.start_time)
            end_dt = dt.datetime.combine(appt.date, appt.end_time)
            diff = (end_dt - start_dt).seconds // 60
            total_minutes += diff

        # Günlük detay
        daily_detail = {}
        for appt in inst_qs.order_by('date', 'start_time'):
            day = appt.date
            if day not in daily_detail:
                daily_detail[day] = {
                    'date': day,
                    'appointments': [],
                    'group_count': 0,
                    'private_count': 0,
                    'total_minutes': 0,
                }
            is_private = appt.user_package.package_type.slug == OZEL_SLUG
            start_dt = dt.datetime.combine(appt.date, appt.start_time)
            end_dt = dt.datetime.combine(appt.date, appt.end_time)
            duration = (end_dt - start_dt).seconds // 60
            daily_detail[day]['appointments'].append({
                'appt': appt,
                'is_private': is_private,
                'duration_min': duration,
            })
            daily_detail[day]['total_minutes'] += duration
            if is_private:
                daily_detail[day]['private_count'] += 1
            else:
                daily_detail[day]['group_count'] += 1

        # Günlük saat/dakika formatla
        for d in daily_detail.values():
            d['hours'] = d['total_minutes'] // 60
            d['mins_rem'] = d['total_minutes'] % 60

        instructor_stats.append({
            'instructor': inst,
            'group_count': group_count,
            'private_count': private_count,
            'total_count': total_count,
            'total_minutes': total_minutes,
            'total_hours': total_minutes // 60,
            'total_mins_rem': total_minutes % 60,
            'daily_detail': sorted(daily_detail.values(), key=lambda x: x['date']),
        })

    # Toplam özet
    grand_group = sum(s['group_count'] for s in instructor_stats)
    grand_private = sum(s['private_count'] for s in instructor_stats)
    grand_total = grand_group + grand_private
    grand_minutes = sum(s['total_minutes'] for s in instructor_stats)

    selected_instructor = None
    if instructor_id:
        try:
            selected_instructor = Instructor.objects.get(pk=instructor_id)
        except Instructor.DoesNotExist:
            pass

    return render(request, 'appointments/instructor_report.html', {
        'instructor_stats': instructor_stats,
        'instructors': instructors,
        'date_from': date_from,
        'date_to': date_to,
        'date_from_str': date_from_str,
        'date_to_str': date_to_str,
        'selected_instructor': selected_instructor,
        'selected_instructor_id': instructor_id,
        'grand_group': grand_group,
        'grand_private': grand_private,
        'grand_total': grand_total,
        'grand_minutes': grand_minutes,
        'grand_hours': grand_minutes // 60,
        'grand_mins_rem': grand_minutes % 60,
        'today': today,
    })


@login_required
def member_packages_json(request):
    from django.http import JsonResponse
    from packages.models import UserPackage
    if not request.user.is_admin_role:
        return JsonResponse({'packages': []})
    member_id = request.GET.get('member_id')
    packages = []
    if member_id:
        pkgs = UserPackage.objects.filter(
            user_id=member_id, is_active=True, remaining_sessions__gt=0
        ).select_related('package_type').order_by('-assigned_at')
        packages = [
            {
                'id': p.pk,
                'label': f'{p.package_type.name} — {p.remaining_sessions}/{p.total_sessions} seans',
            }
            for p in pkgs
        ]
    return JsonResponse({'packages': packages})
