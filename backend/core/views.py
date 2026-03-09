from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from .models import Transaction


# Monthly Summary
class MonthlySummaryView(APIView):
    # Authentication check
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the current date, split year and month
        now = timezone.now()
        this_year = now.year
        this_month = now.month

        # Get the current user from db and the transctions of the current month
        current_month_data = Transaction. objects. filter(
            user = request. user,
            trans_date__year = this_year,
            trans_date__month = this_month
        )

        # Income calculation (amount > 0 : amount__gt=0) 
        # Aggregate(Sum('amount') return format {'amount__sum': XX}
        # Or 0 ensure total returns 0 ecen if there is no data (when month has no transaction)
        income_query = current_month_data.filter(amount__gt = 0) 
        total_income = income_query.aggregate(Sum('amount'))['amount__sum'] or 0 

        # Expense calculation (amount < 0 : amount__lt = 0)
        expense_query = current_month_data.filter(amount__lt = 0)
        total_expense = expense_query.aggregate(Sum('amount'))['amount__sum'] or 0

        # The balance with income and expense
        balance = float(total_income) + float(total_expense)

        # Maintain consistency with front-end.
        result = {
            "period" : f"{this_year}year{this_month}month",
            "income" : float(total_income),
            "expense" : abs(float(total_expense)),
            "net_balance" : balance
        }
        


        # Django REST Framework (DRF) convert dict to Json, and send to browser
        return Response(result)
    
# Pagination & Filter
class TransactionListView(APIView):
    # Authentication check
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all transactions of the user, order by time desc
        transactions = Transaction.objects.filter(user = request.user).order_by('-trans_date')


        # Extract query parameters from the URL and get the parameter value
        # Store in a temporary variable category_id, note_content, start_date, end_date
        # Define parameter names category_id，search，start, end between front-end and back-end
        target_cat_id = request.query_params.get('category_id') # filter by category_id
        target_acc_id = request.query_params.get('account_id') # filter by account
        note_content = request.query_params.get('search') # filter by note
        start_date = request.query_params.get('start') #filter by start date
        end_date = request.query_params.get('end') #filter by end date


        # Filtering in database
        if target_cat_id:
            # Check if url contains category id, if id exists, match the transaction with the corresponding IDs in the database
            transactions = transactions.filter(category_id = target_cat_id)

        if target_acc_id:
            transactions = transactions.filter(account_id=target_acc_id)

        if note_content:
            # Check if url contains search = XXX, match the transaction with the content
            # Note__icontains means fuzzy query in DB note column
            transactions = transactions.filter(note__icontains = note_content)
        
        if start_date:
            # gte = Greater Than or Equal
            transactions = transactions.filter(trans_date__gte = start_date)
        
        if end_date:
            # lte = Less Than or Equal
            transactions = transactions.filter(trans_date__lte = end_date)

        # Pagination
        try:
            # Default page 1 if there is no parameter is provided
            page = int(request.query_params.get('page',1))
            # Default page_size 10 if there is no parameter is provided
            page_size = int(request.query_params.get('page_size', 10))
        except:
            page = 1
            page_size = 10

        # start = (current_page - 1) * page_size
        start = (page - 1) * page_size
        end = start + page_size

        # Only get 10
        current_page_data = transactions[start:end]

        # Serialization：convert to list
        # t is a python object(contains several metadata)
        data_list = []
        for t in current_page_data:
            data_list.append({
                "id" : t.id,
                "amount" : float(t.amount),
                "date": t.trans_date.strftime("%Y-%m-%d %H:%M"),
                "note": t.note,
                "category": t.category.name if t.category else "Unknown",

            })

        return Response({
                "current_page" : page,
                "page_size" : page_size,
                "total_count" : transactions.count(), # total amount, in order to calculate pages
                "data" : data_list
        })







