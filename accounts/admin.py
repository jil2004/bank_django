from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Account, Transaction, Loan

# Customize the User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', 'email')

# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register the Account model
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'account_number', 'account_type', 'balance', 'status')
    search_fields = ('account_number', 'user__username')
    list_filter = ('account_type', 'status')
    actions = ['close_accounts']

    def close_accounts(self, request, queryset):
        queryset.update(status='closed')
    close_accounts.short_description = "Close selected accounts"

# Register the Transaction model
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'transaction_type', 'amount', 'timestamp')
    search_fields = ('account__account_number', 'transaction_type')
    list_filter = ('transaction_type', 'timestamp')

# Register the Loan model
@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'interest_rate', 'status', 'created_at')
    search_fields = ('user__username', 'status')
    list_filter = ('status', 'created_at')
    actions = ['approve_loans', 'reject_loans']

    def approve_loans(self, request, queryset):
        queryset.update(status='approved')
    approve_loans.short_description = "Approve selected loans"

    def reject_loans(self, request, queryset):
        queryset.update(status='rejected')
    reject_loans.short_description = "Reject selected loans"