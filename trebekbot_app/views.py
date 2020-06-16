from django.http import HttpResponse
from src.question import Question


def question(request):
    return HttpResponse(Question(Question.get_random_question()))


def test(request):
    return HttpResponse("Welcome to Trebekbot!")
