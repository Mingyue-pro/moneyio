from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from .models import User, Category, Account


DEFAULT_CATEGORIES = [
    # Expense 一级分类
    {"name": "Food", "category_type": Category.CategoryType.EXPENSE},
    {"name": "Transport", "category_type": Category.CategoryType.EXPENSE},
    {"name": "Shopping", "category_type": Category.CategoryType.EXPENSE},
    {"name": "Entertainment", "category_type": Category.CategoryType.EXPENSE},
    {"name": "Bills", "category_type": Category.CategoryType.EXPENSE},
    {"name": "Health", "category_type": Category.CategoryType.EXPENSE},
    {"name": "Education", "category_type": Category.CategoryType.EXPENSE},
    {"name": "Other Expense", "category_type": Category.CategoryType.EXPENSE},

    # Income 一级分类
    {"name": "Salary", "category_type": Category.CategoryType.INCOME},
    {"name": "Bonus", "category_type": Category.CategoryType.INCOME},
    {"name": "Gift", "category_type": Category.CategoryType.INCOME},
    {"name": "Refund", "category_type": Category.CategoryType.INCOME},
    {"name": "Other Income", "category_type": Category.CategoryType.INCOME},
]

DEFAULT_ACCOUNTS = [
    {"name": "Cash", "account_type": "Cash", "balance": 0.00},
    {"name": "Bank Card", "account_type": "Bank Card", "balance": 0.00},
]


def create_default_categories_for_user(user):
    existing_names = set(
        Category.objects.filter(user=user).values_list("name", flat=True)
    )

    categories = []
    for item in DEFAULT_CATEGORIES:
        if item["name"] not in existing_names:
            categories.append(
                Category(
                    user=user,
                    name=item["name"],
                    category_type=item["category_type"],
                    parent=None,
                    tree_level=1
                )
            )

    if categories:
        Category.objects.bulk_create(categories)


def create_default_accounts_for_user(user):
    existing_names = set(
        Account.objects.filter(user=user).values_list("name", flat=True)
    )

    accounts = []
    for item in DEFAULT_ACCOUNTS:
        if item["name"] not in existing_names:
            accounts.append(
                Account(
                    user=user,
                    name=item["name"],
                    account_type=item["account_type"],
                    balance=item["balance"]
                )
            )

    if accounts:
        Account.objects.bulk_create(accounts)


def register_user(username, email, password):
    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password)
    )

    create_default_categories_for_user(user)
    create_default_accounts_for_user(user)

    return user


def authenticate_user(username, password):
    return authenticate(username=username, password=password)


def update_password(user, new_password):
    user.password = make_password(new_password)
    user.save()
    return user