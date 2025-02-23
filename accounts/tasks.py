from celery import shared_task
from .models import Account

@shared_task
def calculate_interest():
    savings_accounts = Account.objects.filter(account_type='savings')
    for account in savings_accounts:
        account.calculate_interest()