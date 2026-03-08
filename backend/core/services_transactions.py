import decimal

from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime

from .models import Transaction, Account, Category


def _parse_amount(amount_value):
    try:
        amount = decimal.Decimal(str(amount_value))
    except Exception:
        raise ValidationError("amount must be a valid decimal number")

    if amount <= 0:
        raise ValidationError("amount must be greater than 0")

    return amount


def apply_transaction_to_account(account, category, amount):
    if category.category_type == Category.CategoryType.INCOME:
        account.balance += amount
    elif category.category_type == Category.CategoryType.EXPENSE:
        account.balance -= amount
    account.save()


def reverse_transaction_from_account(account, category, amount):
    if category.category_type == Category.CategoryType.INCOME:
        account.balance -= amount
    elif category.category_type == Category.CategoryType.EXPENSE:
        account.balance += amount
    account.save()


def _parse_trans_date(trans_date_str):
    dt = parse_datetime(trans_date_str)
    if not dt:
        raise ValidationError("trans_date must be a valid ISO datetime string")
    return dt


def _get_user_account(user, account_id):
    account = Account.objects.filter(id=account_id, user=user).first()
    if not account:
        raise ValidationError("invalid account_id")
    return account


def _get_user_category(user, category_id):
    category = Category.objects.filter(id=category_id, user=user).first()
    if not category:
        raise ValidationError("invalid category_id")
    return category


def create_transaction_for_user(user, payload):
    account_id = payload.get("account_id")
    category_id = payload.get("category_id")
    amount_value = payload.get("amount")
    trans_date_str = payload.get("trans_date")
    note = payload.get("note", "")

    if not account_id or not category_id or amount_value is None or not trans_date_str:
        raise ValidationError("account_id, category_id, amount and trans_date are required")

    account = _get_user_account(user, account_id)
    category = _get_user_category(user, category_id)
    amount = _parse_amount(amount_value)
    trans_date = _parse_trans_date(trans_date_str)

    tx = Transaction.objects.create(
        user=user,
        account=account,
        category=category,
        amount=amount,
        trans_date=trans_date,
        note=note
    )

    # 关键：联动更新账户余额
    apply_transaction_to_account(account, category, amount)

    return tx


def list_transactions_for_user(user):
    return (
        Transaction.objects
        .filter(user=user)
        .select_related("account", "category")
        .order_by("-trans_date", "-id")
    )


def get_transaction_for_user(user, tx_id):
    return (
        Transaction.objects
        .filter(id=tx_id, user=user)
        .select_related("account", "category")
        .first()
    )


def update_transaction_for_user(user, tx_id, payload):
    tx = get_transaction_for_user(user, tx_id)
    if not tx:
        return None

    old_account = tx.account
    old_category = tx.category
    old_amount = tx.amount

    # 先撤销旧交易对账户余额的影响
    reverse_transaction_from_account(old_account, old_category, old_amount)

    if "account_id" in payload:
        tx.account = _get_user_account(user, payload["account_id"])

    if "category_id" in payload:
        tx.category = _get_user_category(user, payload["category_id"])

    if "amount" in payload:
        tx.amount = _parse_amount(payload["amount"])

    if "trans_date" in payload:
        tx.trans_date = _parse_trans_date(payload["trans_date"])

    if "note" in payload:
        tx.note = payload.get("note", "")

    tx.save()

    # 再应用新交易影响
    apply_transaction_to_account(tx.account, tx.category, tx.amount)

    return tx


def delete_transaction_for_user(user, tx_id):
    tx = get_transaction_for_user(user, tx_id)
    if not tx:
        return False

    # 删除前先撤销余额影响
    reverse_transaction_from_account(tx.account, tx.category, tx.amount)

    tx.delete()
    return True