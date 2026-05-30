from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'transaction_type', 'payment_method', 'description', 'amount', 'created_by']
    list_filter = ['transaction_type', 'payment_method', 'date']
    search_fields = ['description', 'notes']
    date_hierarchy = 'date'
