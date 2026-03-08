from django.http import JsonResponse
from .models import Account


def accounts_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)

    accounts = (
        Account.objects
        .filter(user=request.user)
        .order_by("name")
    )

    results = []
    for account in accounts:
        results.append({
            "id": account.id,
            "name": account.name,
            "account_type": account.account_type,
            "balance": str(account.balance)
        })

    return JsonResponse({"results": results})