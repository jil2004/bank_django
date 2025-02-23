from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Account, Transaction, Loan

# Signup Form
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

# Account Form
class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['account_type']

# Deposit Form
class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']

# Withdrawal Form
class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']

# Transfer Form
class TransferForm(forms.ModelForm):
    to_account = forms.CharField(max_length=20, label="To Account Number")

    class Meta:
        model = Transaction
        fields = ['amount', 'to_account']
        
class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['account', 'amount', 'interest_rate', 'duration_months']