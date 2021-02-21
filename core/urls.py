from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
        path('', views.index, name='index'),
        path('add_expense', views.addExpense, name='add_expense'),
        path('add-category', views.addCategory, name='add_category'),
        path('edit-expense/<int:id>', views.expense_edit, name='edit-expense'),
        path('delete-expense/<int:id>', views.delete_expense, name='delete-expense'),
        path('search-expense', csrf_exempt(views.search_expense), name='search-expense'),
]
