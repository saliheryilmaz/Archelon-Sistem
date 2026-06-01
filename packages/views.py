from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import UserPackage, PackageType
from .forms import AssignPackageForm, EditPackageForm
from accounts.models import CustomUser


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin_role:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def package_list(request):
    packages = UserPackage.objects.select_related('user', 'package_type', 'assigned_by').order_by('-assigned_at')
    members = CustomUser.objects.filter(role='member').order_by('first_name')
    return render(request, 'packages/list.html', {
        'packages': packages,
        'members': members,
    })


@login_required
@admin_required
def assign_package(request):
    form = AssignPackageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        pkg = form.save(commit=False)
        pkg.assigned_by = request.user
        pkg.save()
        messages.success(request, f'{pkg.user} için {pkg.package_type.name} paketi atandı ({pkg.total_sessions} seans).')
        return redirect('packages:list')
    package_types = PackageType.objects.filter(is_active=True)
    return render(request, 'packages/assign.html', {'form': form, 'package_types': package_types})


@login_required
@admin_required
def deactivate_package(request, pk):
    pkg = get_object_or_404(UserPackage, pk=pk)
    pkg.is_active = False
    pkg.save(update_fields=['is_active'])
    messages.success(request, 'Paket devre dışı bırakıldı.')
    return redirect('packages:list')


@login_required
@admin_required
def edit_package(request, pk):
    pkg = get_object_or_404(UserPackage, pk=pk)
    form = EditPackageForm(request.POST or None, instance=pkg)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Paket güncellendi.')
        return redirect('packages:list')
    return render(request, 'packages/edit.html', {'form': form, 'pkg': pkg})



    packages = request.user.packages.select_related('package_type').filter(is_active=True)
    return render(request, 'packages/my_packages.html', {'packages': packages})
