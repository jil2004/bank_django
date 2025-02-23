from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout, views as auth_views
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Account, Transaction, Loan
from .forms import SignUpForm, AccountForm, DepositForm, WithdrawalForm, TransferForm, LoanApplicationForm
from decimal import Decimal

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user to the database
            login(request, user)  # Log the user in
            return redirect('home')  # Redirect to home after signup
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home after login
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login') 

def root_redirect(request):
    # Redirect to the home screen if logged in, otherwise to the login screen
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

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

@login_required
def deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            account_id = request.POST.get('account')
            account = Account.objects.get(id=account_id, user=request.user)  # Ensure the account belongs to the logged-in user
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']

            account.balance += amount
            account.save()

            Transaction.objects.create(
                account=account,
                transaction_type='deposit',
                amount=amount,
                description=description
            )

            return redirect('home')
    else:
        form = DepositForm()

    accounts = Account.objects.filter(user=request.user)  # Show only the logged-in user's accounts
    return render(request, 'accounts/deposit.html', {'form': form, 'accounts': accounts})

@login_required
def withdraw(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            account_id = request.POST.get('account')
            account = Account.objects.get(id=account_id, user=request.user)  # Ensure the account belongs to the logged-in user
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']

            if account.balance >= amount:
                account.balance -= amount
                account.save()

                Transaction.objects.create(
                    account=account,
                    transaction_type='withdrawal',
                    amount=amount,
                    description=description
                )

                return redirect('home')
            else:
                form.add_error('amount', 'Insufficient balance')
    else:
        form = WithdrawalForm()

    accounts = Account.objects.filter(user=request.user)  # Show only the logged-in user's accounts
    return render(request, 'accounts/withdraw.html', {'form': form, 'accounts': accounts})

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

#repay loan
@login_required
def repay_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount'))
        except (TypeError, ValueError):
            return render(request, 'accounts/repay_loan.html', {'loan': loan, 'error': 'Invalid amount.'})

        if amount <= Decimal('0.00'):
            return render(request, 'accounts/repay_loan.html', {'loan': loan, 'error': 'Amount must be greater than 0.'})

        if amount > loan.total_amount:
            return render(request, 'accounts/repay_loan.html', {'loan': loan, 'error': 'Amount cannot exceed the total loan amount.'})

        # Deduct the repaid amount from the loan total amount
        loan.total_amount -= amount
        loan.save()

        # Deduct the repaid amount from the user's account balance
        account = loan.account
        account.balance -= amount
        account.save()

        # Record the repayment transaction
        Transaction.objects.create(
            account=account,
            transaction_type='repayment',
            amount=amount,
            description=f"Repayment for Loan #{loan.id}"
        )

        # Mark the loan as repaid if the total amount is fully repaid
        if loan.total_amount <= Decimal('0.00'):
            loan.status = 'repaid'
            loan.save()

        return redirect('loan_status')

    return render(request, 'accounts/repay_loan.html', {'loan': loan})

@login_required
def loan_details(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)

    # Calculate monthly interest amount
    monthly_interest = (loan.amount * loan.interest_rate / 100) / 12

    # Get all repayment transactions for this loan
    repayments = Transaction.objects.filter(
        account=loan.account,
        transaction_type='repayment',
        description__icontains=f"Repayment for Loan #{loan.id}"
    ).order_by('timestamp')

    context = {
        'loan': loan,
        'monthly_interest': monthly_interest,
        'repayments': repayments,
    }

    return render(request, 'accounts/loan_details.html', context)

@login_required
def account_details(request, account_id):
    account = get_object_or_404(Account, id=account_id, user=request.user)

    # Get all transactions for this account
    transactions = Transaction.objects.filter(account=account).order_by('-timestamp')

    # Get active loans for this account
    active_loans = Loan.objects.filter(account=account, status='approved')

    context = {
        'account': account,
        'transactions': transactions,
        'active_loans': active_loans,
    }

    return render(request, 'accounts/account_details.html', context)

@login_required
def home(request):
    accounts = Account.objects.filter(user=request.user)
    selected_account = accounts.first()  # Default to the first account

    if request.method == 'POST':
        # Handle account selection from the dropdown
        account_id = request.POST.get('account')
        selected_account = get_object_or_404(Account, id=account_id, user=request.user)

    transactions = Transaction.objects.filter(account__user=request.user).order_by('-timestamp')[:3]  # Last 3 transactions
    pending_loans = Loan.objects.filter(user=request.user, status='pending')  # Get pending loans

    # Handle case when no accounts exist
    if not selected_account:
        return render(request, 'accounts/home.html', {
            'accounts': accounts,
            'transactions': transactions,
            'pending_loans': pending_loans,
            'no_accounts': True,  # Add a flag to indicate no accounts
        })

    return render(request, 'accounts/home.html', {
        'accounts': accounts,
        'transactions': transactions,
        'selected_account': selected_account,
        'pending_loans': pending_loans,
        'no_accounts': False,  # Add a flag to indicate accounts exist
    })