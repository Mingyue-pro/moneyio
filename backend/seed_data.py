# seed_data.py
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moneyio.settings')
django.setup()

from core.models import Transaction, Category, Account
from core.models import User

def seed():
    # 1. get tester
    user, _ = User.objects.get_or_create(username='mingyue')
    if _: user.set_password('database12!@'); user.save()

    # 2. get account and category
    acc, _ = Account.objects.get_or_create(user=user, name="HSBC", defaults={'balance': 10000})
    cat_food, _ = Category.objects.get_or_create(user=user, name="Food", category_type="EXPENSE")
    cat_salary, _ = Category.objects.get_or_create(user=user, name="Salary", category_type="INCOME")

    # 3. clear old data and create new data(15)
    Transaction.objects.filter(user=user).delete()
    
    # aad 10 food service income，5 salary income
    for i in range(15):
        is_income = i < 5
        Transaction.objects.create(
            user=user,
            account=acc,
            category=cat_salary if is_income else cat_food,
            amount=random.uniform(5000, 8000) if is_income else -random.uniform(20, 200),
            trans_date=datetime.now() - timedelta(days=random.randint(0, 5)), # 5 days recently
            note=f"test {i} - {'income' if is_income else 'lunch'}"
        )
    print("Success")

if __name__ == '__main__':
    seed()