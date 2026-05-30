from django.contrib import admin
from .models import PackageType, UserPackage


@admin.register(PackageType)
class PackageTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'session_count', 'is_active')
    list_editable = ('is_active',)


@admin.register(UserPackage)
class UserPackageAdmin(admin.ModelAdmin):
    list_display = ('user', 'package_type', 'remaining_sessions', 'total_sessions', 'assigned_by', 'assigned_at', 'is_active')
    list_filter = ('package_type', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('assigned_at', 'total_sessions')
