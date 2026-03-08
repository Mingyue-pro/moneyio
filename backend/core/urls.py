from django.urls import path
from .views_auth import register, login_view, logout_view, current_user, change_password, test_page
from .views_transactions import transactions_collection, transactions_item
from .views_categories import categories_collection, categories_item
from .views_accounts import accounts_list

urlpatterns = [

    path("test/", test_page),# 测试视图
    # Auth
    path("auth/register/", register),
    path("auth/login/", login_view),
    path("auth/logout/", logout_view),
    path("auth/me/", current_user),
    path("auth/change-password/", change_password),
     # Transactions
    path("transactions/", transactions_collection),
    path("transactions/<int:tx_id>/", transactions_item),
     # Categories / Accounts
    path("categories/", categories_collection),
    path("categories/<int:category_id>/", categories_item),
    path("accounts/", accounts_list),
]

