from django.urls import path
from .views import MonthlySummaryView, TransactionListView

urlpatterns = [
    # relative path
    path('summary/', MonthlySummaryView.as_view(), name='monthly_summary'),
    path('list/', TransactionListView.as_view(), name='transaction_list'),
]