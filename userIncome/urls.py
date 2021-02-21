from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
        path('', views.income, name='income'),
        path('add_income', views.add_income, name='add_income'),
        path('add-source', views.addSource, name='add_source'),
        path('income-edit/<int:id>', views.income_edit, name='edit-income'),
        path('income-delete/<int:id>', views.income_delete, name='delete-income'),
        path('search-income', csrf_exempt(views.search_income), name='search-income'),
        ]
