from django.test import TestCase

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import User, Transaction, Category, Account
from django.utils import timezone

class TransactionAPITests(APITestCase):
    def setUp(self):
        # Initialize test data - User, Account, Category
        self.user = User.objects.create_user(username='testadmin', password='password123', email='testadmin@test.com')
        self.client.login(username='testadmin', password='password123')
        
        self.acc = Account.objects.create(user=self.user, name="Test Acc", balance=1000)
        self.cat_income = Category.objects.create(user=self.user, name="Salary", category_type="IN")
        self.cat_expense = Category.objects.create(user=self.user, name="Food", category_type="OUT")

        # Create an income and an expense data

        Transaction.objects.create(
            user=self.user, account=self.acc, category=self.cat_income, 
            amount=100, note="Monthly Salary", trans_date=timezone.now()
        )
        Transaction.objects.create(
            user=self.user, account=self.acc, category=self.cat_expense, 
            amount=40, note="Lunch at Uni", trans_date=timezone.now()
        )

        # Pagination data(total 12)
        for i in range(10):
            Transaction.objects.create(
                user=self.user,
                account=self.acc,
                category=self.cat_expense,
                amount=10,
                note=f"Extra Expense {i}",
                trans_date=timezone.now()
            )

    # Monthly Summary
    def test_monthly_summary(self):
        # find path in urls.py
        url = "/api/transactions/summary/"

        # Calculate monthly summary
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_json = response.json()
        self.assertEqual(float(res_json['income']), 100.0)
        self.assertEqual(float(res_json['expense']), 140.0)
        self.assertEqual(float(res_json['net_balance']), -40.0)
    
    # Monthly summary calculation with new user and 0 transaction
    def test_summary_no_data(self):
        self.client.logout()
        new_user = User.objects.create_user(username='initialisation_user', password='password', email='initialisation_user@test.com')
        self.client.force_login(new_user)

        url = "/api/transactions/summary/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_json = response.json()

        self.assertEqual(float(res_json['income']), 0.0)
        self.assertEqual(float(res_json['expense']), 0.0)
        self.assertEqual(float(res_json['net_balance']), 0.0)

    # Search salary
    def test_transaction_list_search(self):
        url = "/api/transactions/"
        # Basic search
        resp = self.client.get(url, {'search': 'Salary'})
        res_json = resp.json()
        self.assertEqual(len(res_json['results']), 1)
        self.assertEqual(res_json['results'][0]['note'], "Monthly Salary")

        # Fuzzy query search
        resp_fuzzy = self.client.get(url, {'search': 'sal'})
        self.assertEqual(len(resp_fuzzy.json()['results']), 1)

        # No result
        resp_none = self.client.get(url, {'search': 'unknown'})
        self.assertEqual(len(resp_none.json()['results']), 0, "0 items")

    # Category filter
    def test_filter_by_category(self):
        url = "/api/transactions/"
        # Cat_income
        response = self.client.get(url, {'category_id': self.cat_income.id})
        res_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_json['results']), 1)
        self.assertEqual(res_json['results'][0]['category']['name'], "Salary")

    # Account filter
    def test_filter_by_account(self):
        url = "/api/transactions/"
        # Test Acc
        response = self.client.get(url, {'account_id': self.acc.id})
        res_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Default page_size = 10
        self.assertEqual(len(res_json['results']), 10)

    # Date filter
    def test_filter_by_date_range(self):
        url = "/api/transactions/"
        today_date = timezone.localdate()
        today_str = today_date.strftime('%Y-%m-%d')

        # Today
        response_today = self.client.get(url, {'start': today_str})
        self.assertEqual(response_today.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_today.json()['results']), 10)

        # Yesterday
        yesterday_str = (today_date - timezone.timedelta(days=1)).strftime('%Y-%m-%d')
        response_yesterday = self.client.get(url, {'end': yesterday_str})
        self.assertEqual(len(response_yesterday.json()['results']), 0)

    # Pagination
    def test_pagination_out_of_range(self):
        url = "/api/transactions/"
        # Basic Pagination
        resp4 = self.client.get(url, {'page': 3, 'page_size': 5})
        res_json = resp4.json()
        self.assertEqual(resp4.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_json['results']), 2)

        # Pagination overflow
        resp5 = self.client.get(url, {'page': 999, 'page_size': 10})
        res_json = resp5.json()
        self.assertEqual(resp5.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_json['results']), 0)

    # Pagination + Category + Note
    def test_pagination_and_filter_combined(self):
        url = "/api/transactions/"

        # Search 'Extra', category 'Expense', Each page 5 items
        params = {
            'search': 'Extra',
            'category_id': self.cat_expense.id,
            'page': 1,
            'page_size': 5
        }

        response = self.client.get(url, params)
        res_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_json['results']), 5)
        self.assertEqual(res_json['total_count'], 10)
        for item in res_json['results']:
            self.assertIn('Extra', item['note'])


    # Authentication    
    def test_unauthenticated_access(self):
        self.client.logout()
        url = "/api/transactions/summary/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Use data isolation
    def test_data_isolation(self):
        # Create new_user
        new_user = User.objects.create_user(username='new_user', password='password', email='new_user@test.com')
        # Create new_user's account
        acc_new_user = Account.objects.create(user=new_user, name="B's Private Acc", balance=0)
        # Create new_user's category
        cat_b = Category.objects.create(user=new_user, name="B's Cat", category_type="INCOME")
        secret_note = "New_user's Private Secret"
        # Create new_user's transaction
        Transaction.objects.create(
            user=new_user, account=acc_new_user, category=cat_b, 
            amount=5000, note=secret_note, trans_date=timezone.now()
        )
        # Ensure testadmin login
        self.client.force_authenticate(user=self.user)
        url = "/api/transactions/"
        response = self.client.get(url, {'page_size': 20})
        res_json = response.json()

        # Testadmin can browse 12 transaction
        self.assertEqual(len(res_json['results']), 12)
        # Testadmin cannot browse new_user's transaction
        notes = [item['note'] for item in res_json['results']]
        self.assertNotIn("Secret_note", notes)

    
