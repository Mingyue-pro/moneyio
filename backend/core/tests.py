from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Account, Budget, Category, Transaction, User


class TransactionAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testadmin",
            password="password123",
            email="testadmin@test.com",
        )
        self.client.login(username="testadmin", password="password123")

        self.acc = Account.objects.create(
            user=self.user,
            name="Test Acc",
            account_type="Bank Card",
            balance=1000,
        )
        self.cat_income = Category.objects.create(
            user=self.user, name="Salary", category_type="IN"
        )
        self.cat_expense = Category.objects.create(
            user=self.user, name="Food", category_type="OUT"
        )

        Transaction.objects.create(
            user=self.user,
            account=self.acc,
            category=self.cat_income,
            amount=100,
            note="Monthly Salary",
            trans_date=timezone.now(),
        )
        Transaction.objects.create(
            user=self.user,
            account=self.acc,
            category=self.cat_expense,
            amount=40,
            note="Lunch at Uni",
            trans_date=timezone.now(),
        )

        for i in range(10):
            Transaction.objects.create(
                user=self.user,
                account=self.acc,
                category=self.cat_expense,
                amount=10,
                note=f"Extra Expense {i}",
                trans_date=timezone.now(),
            )

    def test_monthly_summary(self):
        url = "/api/transactions/summary/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_json = response.json()
        self.assertEqual(float(res_json["income"]), 100.0)
        self.assertEqual(float(res_json["expense"]), 140.0)
        self.assertEqual(float(res_json["net_balance"]), -40.0)

    def test_summary_no_data(self):
        self.client.logout()
        new_user = User.objects.create_user(
            username="initialisation_user",
            password="password",
            email="initialisation_user@test.com",
        )
        self.client.force_login(new_user)

        url = "/api/transactions/summary/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_json = response.json()

        self.assertEqual(float(res_json["income"]), 0.0)
        self.assertEqual(float(res_json["expense"]), 0.0)
        self.assertEqual(float(res_json["net_balance"]), 0.0)

    def test_transaction_list_search(self):
        url = "/api/transactions/"
        resp = self.client.get(url, {"search": "Salary"})
        res_json = resp.json()
        self.assertEqual(len(res_json["results"]), 1)
        self.assertEqual(res_json["results"][0]["note"], "Monthly Salary")

        resp_fuzzy = self.client.get(url, {"search": "sal"})
        self.assertEqual(len(resp_fuzzy.json()["results"]), 1)

        resp_none = self.client.get(url, {"search": "unknown"})
        self.assertEqual(len(resp_none.json()["results"]), 0)

    def test_filter_by_category(self):
        url = "/api/transactions/"
        response = self.client.get(url, {"category_id": self.cat_income.id})
        res_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_json["results"]), 1)
        self.assertEqual(res_json["results"][0]["category"]["name"], "Salary")

    def test_filter_by_account(self):
        url = "/api/transactions/"
        response = self.client.get(url, {"account_id": self.acc.id})
        res_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_json["results"]), 10)

    def test_filter_by_date_range(self):
        url = "/api/transactions/"
        today_date = timezone.localdate()
        today_str = today_date.strftime("%Y-%m-%d")

        response_today = self.client.get(url, {"start": today_str})
        self.assertEqual(response_today.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_today.json()["results"]), 10)

        yesterday_str = (today_date - timezone.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        response_yesterday = self.client.get(url, {"end": yesterday_str})
        self.assertEqual(len(response_yesterday.json()["results"]), 0)

    def test_pagination_out_of_range(self):
        url = "/api/transactions/"
        resp4 = self.client.get(url, {"page": 3, "page_size": 5})
        res_json = resp4.json()
        self.assertEqual(resp4.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_json["results"]), 2)

        resp5 = self.client.get(url, {"page": 15, "page_size": 10})
        res_json = resp5.json()
        self.assertEqual(resp5.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_json["results"]), 2)

    def test_pagination_and_filter_combined(self):
        url = "/api/transactions/"
        params = {
            "search": "Extra",
            "category_id": self.cat_expense.id,
            "page": 1,
            "page_size": 5,
        }

        response = self.client.get(url, params)
        res_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_json["results"]), 5)
        self.assertEqual(res_json["total_count"], 10)
        for item in res_json["results"]:
            self.assertIn("Extra", item["note"])

    def test_unauthenticated_access(self):
        self.client.logout()
        url = "/api/transactions/summary/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_data_isolation(self):
        new_user = User.objects.create_user(
            username="new_user", password="password", email="new_user@test.com"
        )
        acc_new_user = Account.objects.create(
            user=new_user,
            name="B's Private Acc",
            account_type="Cash",
            balance=0,
        )
        cat_b = Category.objects.create(
            user=new_user, name="B's Cat", category_type="IN"
        )
        secret_note = "New_user's Private Secret"
        Transaction.objects.create(
            user=new_user,
            account=acc_new_user,
            category=cat_b,
            amount=5000,
            note=secret_note,
            trans_date=timezone.now(),
        )
        self.client.force_authenticate(user=self.user)
        url = "/api/transactions/"
        response = self.client.get(url, {"page_size": 20})
        res_json = response.json()

        self.assertEqual(len(res_json["results"]), 12)
        notes = [item["note"] for item in res_json["results"]]
        self.assertNotIn(secret_note, notes)


class AuthMethodConstraintTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="auth_tester",
            password="password123",
            email="auth_tester@test.com",
        )

    def test_logout_only_allows_post(self):
        response = self.client.get("/api/auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json()["error"], "method not allowed")

    def test_me_only_allows_get(self):
        response = self.client.post("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json()["error"], "method not allowed")

    def test_change_password_only_allows_post(self):
        self.client.login(username="auth_tester", password="password123")
        response = self.client.get("/api/auth/change-password/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json()["error"], "method not allowed")

class BudgetAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="budget_user",
            password="password123",
            email="budget_user@test.com",
        )
        self.other_user = User.objects.create_user(
            username="budget_other",
            password="password123",
            email="budget_other@test.com",
        )

        self.user_budget = Budget.objects.create(
            user=self.user,
            name="Food",
            description="Food budget",
            amount_limit="500.00",
            actual_spending="120.00",
            budget_month=timezone.localdate().replace(day=1),
            is_recurring=True,
        )

        self.other_budget = Budget.objects.create(
            user=self.other_user,
            name="Travel",
            description="Travel budget",
            amount_limit="800.00",
            actual_spending="50.00",
            budget_month=timezone.localdate().replace(day=1),
            is_recurring=False,
        )

    def test_budgets_collection_requires_authentication(self):
        response = self.client.get("/api/budgets/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error"], "login required")

    def test_create_budget_returns_expected_shape(self):
        self.client.login(username="budget_user", password="password123")
        payload = {
            "name": "Entertainment",
            "description": "Movies and concerts",
            "amount_limit": "300.00",
            "actual_spending": "40.00",
            "budget_month": "2026-03",
            "is_recurring": False,
        }

        response = self.client.post(
            "/api/budgets/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("budget_id", data)
        self.assertIn("budget", data)
        self.assertEqual(data["budget"]["name"], payload["name"])
        self.assertEqual(data["budget"]["amount_limit"], payload["amount_limit"])

    def test_create_budget_validation_error(self):
        self.client.login(username="budget_user", password="password123")
        payload = {
            "name": "",
            "amount_limit": "200.00",
            "budget_month": "2026-03",
        }

        response = self.client.post(
            "/api/budgets/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"], "name is required")

    def test_update_budget_persists_changes(self):
        self.client.login(username="budget_user", password="password123")
        payload = {
            "name": "Food Updated",
            "amount_limit": "640.00",
            "actual_spending": "280.00",
        }

        response = self.client.patch(
            f"/api/budgets/{self.user_budget.id}/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user_budget.refresh_from_db()
        self.assertEqual(self.user_budget.name, "Food Updated")
        self.assertEqual(str(self.user_budget.amount_limit), "640.00")
        self.assertEqual(str(self.user_budget.actual_spending), "280.00")

    def test_delete_budget_only_removes_current_user_budget(self):
        self.client.login(username="budget_user", password="password123")

        response = self.client.delete(f"/api/budgets/{self.user_budget.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Budget.objects.filter(id=self.user_budget.id).exists())
        self.assertTrue(Budget.objects.filter(id=self.other_budget.id).exists())

    def test_cannot_delete_other_users_budget(self):
        self.client.login(username="budget_user", password="password123")

        response = self.client.delete(f"/api/budgets/{self.other_budget.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Budget.objects.filter(id=self.other_budget.id).exists())

class UserModelTests(TestCase):
    #Test User Model
    def test_create_user(self):
        user = User.objects.create_user(
             username="modelusercreation",
             password="password",
             email='modelcreateuser@test.com',
        )
        self.assertEqual(user.username, "modelusercreation")
        self.assertEqual(user.email, "modelcreateuser@test.com")
        self.assertIsNotNone(user.reg_date)

    def test_user_str(self):
        # Return username
        user = User.objects.create_user(
            username="struser", password="x", email="struser@test.com"
        )
        self.assertEqual(str(user), "struser")

class AccountModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="accountuser", password="accounttest", email="accountuser@test.com"
        )
        acc = Account.objects.create(
            user = self.user,
            name = "Bank",
            account_type = "Bank Card",
            balance = Decimal("2026.03"),
        )
        self.assertEqual(acc.name, "Bank")
        self.assertEqual(acc.balance, Decimal("2026.03"))

    def test_account_default_balance(self):
        acc = Account.objects.create(
            user = self.user, name = "Cash", account_type = "Cash"
        )
        self.assertEqual(acc.balance, Decimal("0.00"))

    def test_account_str(self):
        acc = Account.objects.create(
            user = self.user, name = "Test Account", account_type = "Card"
        )
        self.assertEqual(str(acc), "Test Account")

    def test_account_related_transactions(self):
        acc = Account.objects.create(
            user=self.user, name="Account", account_type="Card"
        )
        self.assertEqual(acc.transactions.count(), 0)

class CategoryModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="categoryuser", password="testAAA12!@", email="categoryuser@test.com"
        )

    def test_create_income_category(self):
        cat = Category.objects.create(
            user=self.user, name="Salary", category_type=Category.CategoryType.INCOME
        )
        self.assertEqual(cat.category_type, "IN")

    def test_create_expense_category(self):
        cat = Category.objects.create(
            user=self.user, name="Food", category_type=Category.CategoryType.EXPENSE
        )
        self.assertEqual(cat.category_type, "OUT")

    def test_category_str(self):
        cat = Category.objects.create(
            user=self.user, name="Market", category_type=Category.CategoryType.EXPENSE
        )
        self.assertEqual(str(cat), "Market")

    def test_category_default_tree_level(self):
        cat = Category.objects.create(
            user=self.user, name="Cat", category_type=Category.CategoryType.INCOME
        )
        self.assertEqual(cat.tree_level, 1)

class TransactionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="transuser", password="transaction", email="transuser@test.com"
        )
        self.acc = Account.objects.create(
            user=self.user, name="Acc", account_type="Card"
        )
        self.cat = Category.objects.create(
            user=self.user, name="Cat", category_type=Category.CategoryType.INCOME
        )

    def test_create_transaction(self):
        tx = Transaction.objects.create(
            user=self.user,
            account=self.acc,
            category=self.cat,
            amount=Decimal("2026.03"),
            trans_date=timezone.now(),
            note="Test note",
        )
        self.assertEqual(tx.amount, Decimal("2026.03"))
        self.assertEqual(tx.note, "Test note")
        self.assertIsNotNone(tx.crt_time)
        self.assertIsNotNone(tx.upt_time)

    def test_transaction_str_format(self):
        tx = Transaction.objects.create(
            user=self.user,
            account=self.acc,
            category=self.cat,
            amount=Decimal("100.00"),
            trans_date=timezone.now(),
        )
        s = str(tx)
        self.assertIn(self.cat.name, s)
        self.assertIn("100.00", s)

class BudgetModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="budgetuser", password="x", email="budgetuser@test.com"
        )

    def test_create_budget(self):
        from datetime import date
        b = Budget.objects.create(
            user=self.user,
            amount_limit=Decimal("3000.00"),
            budget_month=date(2026, 3, 1),
            is_recurring=True,
        )
        self.assertEqual(b.amount_limit, Decimal("3000.00"))
        self.assertEqual(b.actual_spending, Decimal("0.00"))
        self.assertTrue(b.is_recurring)

    def test_budget_str(self):
        from datetime import date
        b = Budget.objects.create(
            user=self.user,
            amount_limit=Decimal("1000.00"),
            budget_month=date(2026, 3, 1),
        )
        self.assertIn("2026", str(b))
        self.assertIn("Budget", str(b))
