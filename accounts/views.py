from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Account, Transaction, Loan
from .forms import SignUpForm, AccountForm, DepositForm, WithdrawalForm, TransferForm, LoanApplicationForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home') 
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')  

def home(request):
    return render(request, 'accounts/home.html')

def create_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.account_number = f"{request.user.id}{Account.objects.count() + 1}"  # Simple account number generation
            account.save()
            return redirect('view_account')
    else:
        form = AccountForm()
    return render(request, 'accounts/create_account.html', {'form': form})

def view_account(request):
    accounts = Account.objects.filter(user=request.user)
    return render(request, 'accounts/view_account.html', {'accounts': accounts})

def deposit(request, account_id):
    account = Account.objects.get(id=account_id)
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            account.balance += amount
            account.save()
            Transaction.objects.create(account=account, transaction_type='deposit', amount=amount)
            return redirect('view_account')
    else:
        form = DepositForm()
    return render(request, 'accounts/deposit.html', {'form': form, 'account': account})

def withdraw(request, account_id):
    account = Account.objects.get(id=account_id)
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if account.balance >= amount:
                account.balance -= amount
                account.save()
                Transaction.objects.create(account=account, transaction_type='withdrawal', amount=amount)
                return redirect('view_account')
            else:
                form.add_error('amount', 'Insufficient balance')
    else:
        form = WithdrawalForm()
    return render(request, 'accounts/withdraw.html', {'form': form, 'account': account})

def transfer(request, account_id):
    account = Account.objects.get(id=account_id)
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            to_account_number = form.cleaned_data['to_account']
            try:
                to_account = Account.objects.get(account_number=to_account_number)
                if account.balance >= amount:
                    account.balance -= amount
                    to_account.balance += amount
                    account.save()
                    to_account.save()
                    Transaction.objects.create(account=account, transaction_type='transfer', amount=amount, description=f"Transferred to {to_account_number}")
                    Transaction.objects.create(account=to_account, transaction_type='transfer', amount=amount, description=f"Received from {account.account_number}")
                    return redirect('view_account')
                else:
                    form.add_error('amount', 'Insufficient balance')
            except Account.DoesNotExist:
                form.add_error('to_account', 'Account does not exist')
    else:
        form = TransferForm()
    return render(request, 'accounts/transfer.html', {'form': form, 'account': account})

def transaction_history(request, account_id):
    account = Account.objects.get(id=account_id)
    transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
    return render(request, 'accounts/transaction_history.html', {'transactions': transactions, 'account': account})

@login_required
def apply_for_loan(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.save()
            return redirect('loan_status')
    else:
        form = LoanApplicationForm()
    return render(request, 'accounts/apply_for_loan.html', {'form': form})

# View loan status
@login_required
def loan_status(request):
    loans = Loan.objects.filter(user=request.user)
    return render(request, 'accounts/loan_status.html', {'loans': loans})