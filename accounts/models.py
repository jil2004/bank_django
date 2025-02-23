from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

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
    return_date = models.DateField(null=True, blank=True)  # Add return date field
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    loan_duration = models.IntegerField(help_text="Duration in months", default=12)  # Add loan duration field

    def __str__(self):
        return f"Loan #{self.id} - {self.user.username}"

    def save(self, *args, **kwargs):
        # Update balance, calculate total amount, and set return date when loan is approved
        if self.status == 'approved' and self.pk is not None:
            original_loan = Loan.objects.get(pk=self.pk)
            if original_loan.status != 'approved':  # Check if status changed to approved
                # Update account balance
                account = Account.objects.get(user=self.user)
                account.balance += self.amount
                account.save()

                # Calculate total amount (principal + interest)
                self.total_amount = self.amount + (self.amount * self.interest_rate / 100)

                # Calculate return date
                self.return_date = self.created_at + timedelta(days=30 * self.loan_duration)

        super().save(*args, **kwargs)