from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
#from django.shortcuts import get_object_or_404

# Create your views here.
def search_expense(request):
    if request.method == 'POST':

        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(amount__istartswith=search_str, user = request.user) | Expense.objects.filter(
                date__istartswith=search_str, user = request.user) | Expense.objects.filter(
                        description__icontains=search_str, user = request.user) | Expense.objects.filter(

                                category__icontains=search_str, user = request.user)

        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(user=request.user)

    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency 
    context = {
            'expense': expenses,
            'page_obj': page_obj,
            'currency': currency
            }
    return render(request, 'expenses/index.html', context)

def addExpense(request):
    categories = Category.objects.all()
    context = {
            'categories': categories,
            'values': request.POST
            }

    if request.method == "GET":
        return render(request, 'expenses/add_expense.html', context)

    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, 'expenses/add_expense.html', context)

        description = request.POST["description"]
        date = request.POST["expense_date"]
        category = request.POST["category"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(user=request.user, amount=amount, date=date, description=description, category=category)
        messages.success(request, "Expense saved Succefully")
        return redirect('index')


def expense_edit(request, id):
    categories = Category.objects.all()
    expense = Expense.objects.get(pk=id)
    context = {
            'expense': expense,
            'values': expense,
            'categories': categories,
            }
    if request.method == "GET":
        return render(request, 'expenses/edit_expense.html', context)

    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, 'expenses/edit_expense.html', context)

        description = request.POST["description"]
        date = request.POST["expense_date"]
        category = request.POST["category"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, 'expenses/edit_expense.html', context)

        expense.user=request.user 
        expense.amount=amount
        expense.date=date
        expense.description=description
        expense.category=category

        expense.save()
        messages.success(request, "Expense updated Succefully")
        return redirect('index')

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('index')
