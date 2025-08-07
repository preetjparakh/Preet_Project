from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    peoples = [
        {'name': 'John', 'age': 30},
        {'name': 'Alice', 'age': 25},
        {'name': 'Bob', 'age': 40}
    ]
    return render(request, "index.html", context={'peoples': peoples})

def success_page(request):
    return HttpResponse("this is success")
