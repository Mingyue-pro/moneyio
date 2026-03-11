import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Transaction
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator

from .services_transactions import (
    create_transaction_for_user,
    list_transactions_for_user,
    get_transaction_for_user,
    update_transaction_for_user,
    delete_transaction_for_user,
)



def _require_login(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)
    return None

# Pagination & Filter & Search
@csrf_exempt
def transactions_collection(request):
    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        # Get all transactions of the user, order by time desc
        transactions = (
            Transaction.objects
            .filter(user=request.user)
            .select_related('account','category')
            .order_by('-trans_date')
        )

        # Extract query parameters from the URL and get the parameter value
        # Store in a temporary variable category_id, note_content, start_date, end_date
        # Define parameter names category_id，search，start, end between front-end and back-end
        raw_cat_id = request.GET.get('category_id')
        raw_acc_id = request.GET.get('account_id')
        note_content = request.GET.get('search')
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')

        # Filtering & Search
        # Validate and coerce ID query parameters to integers
        target_cat_id = None
        if raw_cat_id is not None:
            try:
                target_cat_id = int(raw_cat_id)
            except(TypeError, ValueError):
                return JsonResponse({"error": "Invalid category_id"}, status=400)
            
        if target_cat_id is not None:
            # Check if url contains category id, if id exists, match the transaction with the corresponding IDs in the database
            transactions = transactions.filter(category_id=target_cat_id)
        
        target_acc_id = None
        if raw_acc_id is not None:
            try:
                target_acc_id = int(raw_acc_id)
            except(TypeError, ValueError):
                return JsonResponse({"error": "Invalid account_id"}, status = 400)    
        if target_acc_id is not None:
            transactions = transactions.filter(account_id=target_acc_id)
        if note_content:
            # Check if url contains search = XXX, match the transaction with the content
            # Note__icontains means fuzzy query in DB note column
            transactions = transactions.filter(note__icontains=note_content)
        if start_date:
            #convert String to date object,then convert to datetime with timezone
            d = parse_date(start_date)
            if d:
                aware_start = timezone.make_aware(timezone.datetime.combine(d, timezone.datetime.min.time()))
                # gte = Greater Than or Equal
                transactions = transactions.filter(trans_date__gte=aware_start)
        if end_date:
            d = parse_date(end_date)
            if d:
                aware_end = timezone.make_aware(timezone.datetime.combine(d, timezone.datetime.max.time()))
                # lte = Less Than or Equal
                transactions = transactions.filter(trans_date__lte=aware_end)

        # Pagination
        # Page size limitation
        PAGE_SIZE_MAX = 100
        try:
            # Default page 1 if there is no parameter is provided
            page = int(request.GET.get('page', 1))
            # Default page_size 10 if there is no parameter is provided
            page_size = int(request.GET.get('page_size', 10))
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Invalid page or page_size parameter"},
                status = 400
            )

        if page < 1 or page_size < 1 or page_size > PAGE_SIZE_MAX:
            return JsonResponse(
                {"error": "Page must >=1, page_size must be between 1 and {}".format(PAGE_SIZE_MAX)},
                status = 400
            )

        paginator = Paginator(transactions, per_page=page_size)
        page_obj = paginator.get_page(page)  # 超出范围时自动落到最后一页或空页，不会 500
        current_page_data = page_obj.object_list

        # Serialization：convert to list
        # t is a python object(contains several metadata)
        results = []
        for t in current_page_data:
            results.append({
                "id": t.id,
                "amount": str(t.amount),
                "trans_date": t.trans_date.isoformat(),
                "note": t.note,
                "account": {
                    "id": t.account.id,
                    "name": t.account.name,
                    "account_type": t.account.account_type,
                    "balance": str(t.account.balance),
                },
                "category": {
                    "id": t.category.id,
                    "name": t.category.name,
                    "category_type": t.category.category_type,
                } if t.category else None,
            })

        return JsonResponse({
            "current_page": page,
            "page_size": page_size,
            "total_count": transactions.count(),
            "results": results
        })

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            tx = create_transaction_for_user(request.user, data)
            return JsonResponse({"status": "success", "transaction_id": tx.id})
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid JSON"}, status=400)
        except ValidationError as e:
            return JsonResponse({"error": e.message}, status=400)

    return JsonResponse({"error": "method not allowed"}, status=405)


@csrf_exempt
def transactions_item(request, tx_id):
    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        tx = get_transaction_for_user(request.user, tx_id)
        if not tx:
            return JsonResponse({"error": "not found"}, status=404)

        return JsonResponse({
            "id": tx.id,
            "amount": str(tx.amount),
            "trans_date": tx.trans_date.isoformat(),
            "note": tx.note,
            "account_id": tx.account.id,
            "category_id": tx.category.id,
        })

    if request.method in ("PUT", "PATCH"):
        try:
            data = json.loads(request.body)
            tx = update_transaction_for_user(request.user, tx_id, data)
            if not tx:
                return JsonResponse({"error": "not found"}, status=404)
            return JsonResponse({"status": "success"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid JSON"}, status=400)
        except ValidationError as e:
            return JsonResponse({"error": e.message}, status=400)

    if request.method == "DELETE":
        ok = delete_transaction_for_user(request.user, tx_id)
        if not ok:
            return JsonResponse({"error": "not found"}, status=404)
        return JsonResponse({"status": "deleted"})

    return JsonResponse({"error": "method not allowed"}, status=405)

# Monthly Summary
@csrf_exempt
def transactions_summary(request):

    auth_error = _require_login(request)
    if auth_error:
        return auth_error
    
    # Get the current date, split year and month
    if request.method == "GET":
        now = timezone.localtime(timezone.now())
        # Extract year/month
        this_year = now.year
        this_month = now.month

        #Compute the dateime range for the current month in the active timezone
        start_of_month = now.replace(day=1, hour=0, minute =0, second=0, microsecond=0)
        if this_month == 12:
            start_of_next_month = start_of_month.replace(year=this_year+1, month = 1)
        else:
            start_of_next_month = start_of_month.replace(month = this_month +1)

        # Get the current user from db and the transctions of the current month
        current_month_data = Transaction.objects.filter(
            user=request.user,
            trans_date__gte=start_of_month,
            trans_date__lt=start_of_next_month
        )
        # Income calculation
        # Aggregate(Sum('amount') return format {'amount__sum': XX}
        # Or 0 ensure total returns 0 ecen if there is no data (when month has no transaction)
        income_data = current_month_data.filter(category__category_type='IN').aggregate(Sum('amount'))
        total_income = income_data['amount__sum'] or 0.0

        # Expense calculation 
        expense_data = current_month_data.filter(category__category_type='OUT').aggregate(Sum('amount'))
        total_expense = expense_data['amount__sum'] or 0.0

        # The balance with income and expense
        balance = float(total_income) - float(total_expense)

        # Maintain consistency with front-end.
        return JsonResponse({
            "period": f"{this_year}-{this_month:02d}",
            "income": str(total_income),
            "expense": str(abs(total_expense)),
            "net_balance": str(balance)
        })

    return JsonResponse({"error": "method not allowed"}, status=405)
