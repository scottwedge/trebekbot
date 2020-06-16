from django.http import HttpResponse
from src.question import Question


def test(request):
    return HttpResponse("Welcome to Trebekbot!")


def question(request):
    return Question().format_slack_text()