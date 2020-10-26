from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('add_expense', views.addExpense, name='add_expense'),
]
