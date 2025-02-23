from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('create-account/', views.create_account, name='create_account'),
    path('view-account/', views.view_account, name='view_account'),
    path('deposit/<int:account_id>/', views.deposit, name='deposit'),
    path('withdraw/<int:account_id>/', views.withdraw, name='withdraw'),
    path('transfer/<int:account_id>/', views.transfer, name='transfer'),
    path('transaction-history/<int:account_id>/', views.transaction_history, name='transaction_history'),
    path('apply-for-loan/', views.apply_for_loan, name='apply_for_loan'),
    path('loan-status/', views.loan_status, name='loan_status'),
    path('repay-loan/<int:loan_id>/', views.repay_loan, name='repay_loan'),
    path('loan-details/<int:loan_id>/', views.loan_details, name='loan_details'),
    path('account-details/<int:account_id>/', views.account_details, name='account_details'),
]