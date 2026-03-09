from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import User, Transaction, Category, Account
from django.utils import timezone

# Create your tests here.
class TransactionAPITests(APITestCase):
    def setUp(self):
        # Initialize test data - User, Account, Category
        self.user = User.objects.create_user(username='testadmin', password='password123', email='testadmin@test.com')
        self.client.login(username='testadmin', password='password123')
        
        self.acc = Account.objects.create(user=self.user, name="Test Acc", balance=1000)
        self.cat_income = Category.objects.create(user=self.user, name="Salary", category_type="INCOME")
        self.cat_expense = Category.objects.create(user=self.user, name="Food", category_type="EXPENSE")

        # Create an income and an expense data

        Transaction.objects.create(
            user=self.user, account=self.acc, category=self.cat_income, 
            amount=100, note="Monthly Salary", trans_date=timezone.now()
        )
        Transaction.objects.create(
            user=self.user, account=self.acc, category=self.cat_expense, 
            amount=-40, note="Lunch at Uni", trans_date=timezone.now()
        )

        # Pagination data(total 12)
        for i in range(10):
            Transaction.objects.create(
            user=self.user,
            account=self.acc,
            category=self.cat_expense,
            amount=-10,
            note=f"Extra Expense {i}",
            trans_date=timezone.now()
        )

    # Monthly Summary
    def test_monthly_summary(self):
        # find path in urls.py
        url = reverse('monthly_summary')

        # Calculate monthly summary
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['income'], 100.0)
        self.assertEqual(response.data['expense'], 140.0)
        self.assertEqual(response.data['net_balance'], -40.0)
    
    # Monthly summary calculation with new user and 0 transaction
    def test_summary_no_data(self):
        new_user = User.objects.create_user(username='initialisation_user', password='password', email='initialisation_user@test.com')
        self.client.force_authenticate(user=new_user)
        url = reverse('monthly_summary')
        response = self.client.get(url)
        self.assertEqual(response.data['income'], 0.0)
        self.assertEqual(response.data['expense'], 0.0)
        self.assertEqual(response.data['net_balance'], 0.0)

    # Search salary
    def test_transaction_list_search(self):
        url = reverse('transaction_list')

        # Basic search
        resp1 = self.client.get(url, {'search': 'Salary'})
        self.assertEqual(len(resp1.data['data']), 1, "return 1 result")

        # Fuzzy query search
        resp2 = self.client.get(url, {'search': 'sal'})
        self.assertEqual(len(resp2.data['data']), 1, "ignore fuzzy query return 1 result")

        # No result
        resp3 = self.client.get(url, {'search': 'unknown'})
        self.assertEqual(len(resp3.data['data']), 0, "0 items")

    # Category filter
    def test_filter_by_category(self):
        url = reverse('transaction_list')
        # Cat_income
        response = self.client.get(url, {'category_id': self.cat_income.id})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['note'], "Monthly Salary")

    # Account filter
    def test_filter_by_account(self):
        url = reverse('transaction_list')
        # Test Acc
        response = self.client.get(url, {'account_id': self.acc.id})
        self.assertEqual(response.status_code, 200)
        # Default page_size = 10
        self.assertEqual(len(response.data['data']), 10)

    # Date filter
    def test_filter_by_date_range(self):
        url = reverse('transaction_list')
        today_obj = timezone.localdate()
        today_str = timezone.now().strftime('%Y-%m-%d')

        # Today
        response = self.client.get(url, {'start': today_str})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['data']), 0)

        # Yesterday
        yesterday_obj = today_obj - timezone.timedelta(days=1)
        response_yesterday = self.client.get(url, {'end': yesterday_obj.strftime('%Y-%m-%d')})
        self.assertEqual(len(response_yesterday.data['data']), 0)

    # Pagination
    def test_pagination_out_of_range(self):
        url = reverse('transaction_list')

        # Basic Pagination
        resp4 = self.client.get(url, {'page': 3, 'page_size': 5})
        self.assertEqual(resp4.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp4.data['data']), 2)

        # Pagination overflow
        resp5 = self.client.get(url, {'page': 999, 'page_size': 10})
    
        self.assertEqual(resp5.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp5.data['data']), 0)

    # Pagination + Category + Note
    def test_pagination_and_filter_combined(self):
        url = reverse('transaction_list')

        # Search 'Extra', category 'Expense', Each page 5 items
        params = {
            'search': 'Extra',
            'category_id': self.cat_expense.id,
            'page': 1,
            'page_size': 5
        }

        response = self.client.get(url, params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 5)
        self.assertEqual(response.data['total_count'], 10)
        for item in response.data['data']:
            self.assertIn('Extra', item['note'])


    # Authentication    
    def test_unauthenticated_access(self):
        self.client.logout()
        url = reverse('monthly_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Use data isolation
    def test_data_isolation(self):
        # Create new_user
        new_user = User.objects.create_user(username='new_user', password='password', email='new_user@test.com')
        # Create new_user's account
        acc_new_user = Account.objects.create(user=new_user, name="B's Private Acc", balance=0)
        # Create new_user's category
        cat_b = Category.objects.create(user=new_user, name="B's Cat", category_type="INCOME")
        
        # Create new_user's transaction
        Transaction.objects.create(
            user=new_user, account=acc_new_user, category=cat_b, 
            amount=5000, note="New_user's Private Secret", trans_date=timezone.now()
        )
        # Ensure testadmin login
        self.client.force_authenticate(user=self.user)

        url = reverse('transaction_list')
        response = self.client.get(url, {'page_size': 20})
        # Testadmin can browse 12 transaction
        self.assertEqual(len(response.data['data']), 12)
        # Testadmin cannot browse new_user's transaction
        for item in response.data['data']:
            self.assertNotEqual(item['note'], "New_user's Private Secret")

    
