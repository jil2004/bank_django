from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=[('savings', 'Savings'), ('current', 'Current')])
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    last_interest_calculation = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('closed', 'Closed')], default='active')

    def calculate_interest(self):
        if self.account_type == 'savings' and self.balance > 0:
            now = timezone.now()
            if self.last_interest_calculation:
                days_since_last_calculation = (now - self.last_interest_calculation).days
            else:
                days_since_last_calculation = (now - self.created_at).days
            interest_rate = 0.05  # 5% annual interest rate
            daily_interest = (self.balance * interest_rate) / 365
            self.balance += daily_interest * days_since_last_calculation
            self.last_interest_calculation = now
            self.save()
    
    def __str__(self):
        return f"{self.account_number} - {self.user.username}"

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'), ('transfer', 'Transfer')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
    
class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan #{self.id} - {self.user.username}"
    
