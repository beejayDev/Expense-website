from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
#from django.shortcuts import get_object_or_404
import datetime

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

#List all the Expenses
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

#Create an Expense
@login_required(login_url='/login')
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

@login_required(login_url='/login')
def addCategory(request):
    if request.method == "GET":
        category = Category.objects.all()
        context = {
            'categories': category
        }
        return render(request, 'expenses/add_category.html', context)

    if request.method == "POST":
        category = request.POST['category']

        if not category:
            messages.error(request, 'Category can not be empty')
            return render(request, 'expenses/add_category.html')

        Category.objects.create(name=category)
        messages.success(request, 'Category saved successfully')
        return redirect('add_expense')

#Edit an Expense
@login_required(login_url='/login')
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

#Delete Expense
@login_required(login_url='/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('index')

def expense_category_summary(request):
    tday_date = datetime.date.today()
    six_month_ago = tday_date - datetime.timedelta(days = 30 * 6)
    
    expense = Expense.object.filter(user = request.user,
        date__gte = six_month_ago, date__lte = tday_date)
    finalrep = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))
    
    def get_expense_category_amount(category):
        amount = 0
        filterd_by_category = expense.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)
    return JsonResponse({'expense_category_data': finalrep }, safe=false)

def stats_view(request):
    return render(request, 'expenses/stats.html') 