from django.http import HttpResponse
from django.shortcuts import

def test(request):
    return HttpResponse("Welcome to Trebekbot!")

