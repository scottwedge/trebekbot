# django
from django.http import HttpResponse
from ..models import Question

# native
from os import path, pardir
project_root = path.join(path.dirname(path.abspath(__file__)), pardir)


def question(request):

    # gets random question from given json file
    jeopardy_json_file = open(path.join(project_root, 'support_files', 'JEOPARDY_QUESTIONS1.json')).read()
    question_list = json.loads(jeopardy_json_file)
    question_json = question_list[randint(0, len(question_list))]

    new_question = Question(
        text = question_json['question'],
        value = question_json['value'],
        category = question_json['category'],
        #daily_double = ?
        answer = question_json['answer'],
        date = question_json['air_date']
    )
    return HttpResponse(new_question)


def test(request):
    return HttpResponse("Welcome to Trebekbot!")
