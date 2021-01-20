from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, Income
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
import json
from django.http import JsonResponse

# Create your views here.
def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = Income.objects.filter(amount__istartswith=search_str, user = request.user) | Income.objects.filter(
                date__istartswith=search_str, user = request.user) | Income.objects.filter(
                        description__icontains=search_str,user = request.user) | Income.objects.filter(
                                source__icontains=search_str, user = request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/login')
def income(request):
    sources = Source.objects.all()
    income = Income.objects.filter(user=request.user)
    currency = UserPreference.objects.get(user=request.user).currency
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    context = {
            'income': income,
            'page_obj': page_obj,
            'currency': currency
            }
    return render(request, 'income/index.html', context)

def add_income(request):
    sources = Source.objects.all()
    context = {
            'sources': sources,
            'values': request.POST
            }

    if request.method == "GET":
        return render(request, 'income/add_income.html',context)

    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, 'income/add_income.html', context)

        description = request.POST["description"]
        date = request.POST["income_date"]
        source = request.POST["source"]
        print(request.POST)

        if not description:
            messages.error(request, "Description is required")
            return render(request, 'income/add_income.html', context)
        Income.objects.create(user=request.user, amount=amount, date=date, description=description, source=source)
        messages.success(request, "Record saved Succefully")
        return redirect('income')


def income_edit(request, id):
    sources = Source.objects.all()
    income= Income.objects.get(pk=id)
    context = {
            'income': income,
            'values': income,
            'sources': sources
            }

    if request.method == "GET":
        return render(request, 'income/edit_income.html', context)

    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, 'income/edit_income.html', context)

        description = request.POST["description"]
        date = request.POST["income_date"]
        source = request.POST["source"]

        if not description:
            messages.error(request, "Description is require")
            return render(request, 'income/edit_income.html', context)

        income.user=request.user
        income.amount=amount
        income.date=date
        income.description=description
        income.source=source
        income.save()

        messages.success(request, "Record updated Succefully")
        return redirect('income')

def income_delete(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Record removed')
    return redirect('income')

