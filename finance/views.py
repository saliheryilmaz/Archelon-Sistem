from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Transaction
from .forms import TransactionForm
import datetime


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin_role:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def transaction_list(request):
    today = timezone.now().date()

    # Filtreler
    filter_type = request.GET.get('tur', '')
    filter_method = request.GET.get('yontem', '')
    filter_month = request.GET.get('ay', '')
    filter_year = request.GET.get('yil', str(today.year))

    qs = Transaction.objects.select_related('created_by')

    if filter_type in ('gelir', 'gider'):
        qs = qs.filter(transaction_type=filter_type)
    if filter_method in ('nakit', 'havale'):
        qs = qs.filter(payment_method=filter_method)
    if filter_year:
        qs = qs.filter(date__year=filter_year)
    if filter_month:
        qs = qs.filter(date__month=filter_month)

    # Özet hesapları (filtrelenmiş)
    total_income = qs.filter(transaction_type='gelir').aggregate(t=Sum('amount'))['t'] or 0
    total_expense = qs.filter(transaction_type='gider').aggregate(t=Sum('amount'))['t'] or 0
    net = total_income - total_expense

    # Nakit / Havale ayrımı (filtrelenmiş)
    cash_income = qs.filter(transaction_type='gelir', payment_method='nakit').aggregate(t=Sum('amount'))['t'] or 0
    transfer_income = qs.filter(transaction_type='gelir', payment_method='havale').aggregate(t=Sum('amount'))['t'] or 0
    cash_expense = qs.filter(transaction_type='gider', payment_method='nakit').aggregate(t=Sum('amount'))['t'] or 0
    transfer_expense = qs.filter(transaction_type='gider', payment_method='havale').aggregate(t=Sum('amount'))['t'] or 0

    # Yıl seçenekleri
    years = (
        Transaction.objects.dates('date', 'year', order='DESC')
        .values_list('date__year', flat=True)
    )
    year_list = list(dict.fromkeys([d.year for d in Transaction.objects.dates('date', 'year', order='DESC')]))
    if not year_list:
        year_list = [today.year]

    months = [
        (1, 'Ocak'), (2, 'Şubat'), (3, 'Mart'), (4, 'Nisan'),
        (5, 'Mayıs'), (6, 'Haziran'), (7, 'Temmuz'), (8, 'Ağustos'),
        (9, 'Eylül'), (10, 'Ekim'), (11, 'Kasım'), (12, 'Aralık'),
    ]

    context = {
        'transactions': qs,
        'total_income': total_income,
        'total_expense': total_expense,
        'net': net,
        'cash_income': cash_income,
        'transfer_income': transfer_income,
        'cash_expense': cash_expense,
        'transfer_expense': transfer_expense,
        'filter_type': filter_type,
        'filter_method': filter_method,
        'filter_month': filter_month,
        'filter_year': filter_year,
        'year_list': year_list,
        'months': months,
    }
    return render(request, 'finance/list.html', context)


@login_required
@admin_required
def transaction_create(request):
    initial = {'date': timezone.now().date()}
    form = TransactionForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        t = form.save(commit=False)
        t.created_by = request.user
        t.save()
        messages.success(request, 'İşlem başarıyla kaydedildi.')
        return redirect('finance:list')
    return render(request, 'finance/form.html', {'form': form, 'title': 'Yeni İşlem'})


@login_required
@admin_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    form = TransactionForm(request.POST or None, instance=transaction)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'İşlem güncellendi.')
        return redirect('finance:list')
    return render(request, 'finance/form.html', {'form': form, 'title': 'İşlemi Düzenle', 'transaction': transaction})


@login_required
@admin_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'İşlem silindi.')
        return redirect('finance:list')
    return render(request, 'finance/confirm_delete.html', {'transaction': transaction})
