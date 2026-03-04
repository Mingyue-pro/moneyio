from django.contrib import admin
from .models import User, Account, Category, Transaction, Budget
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'reg_date')
    readonly_fields = ('reg_date',)
    search_fields = ('username', 'email')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Info', {'fields': ('reg_date',)}),
    )
        

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'account_type', 'balance')
    list_filter = ('account_type',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('trans_date', 'category', 'amount', 'account', 'user')
    date_hierarchy = 'trans_date'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'parent')
    list_filter = ('category_type',)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'budget_month', 'amount_limit', 'actual_spending', 'upt_time')
    