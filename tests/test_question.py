import os
from sys import path as syspath
syspath.append(
os.path.abspath(
os.path.join(
os.path.dirname(__file__), os.path.pardir)))
from src import question
from threading import Timer
import pytest
import json


test_timer = Timer(1, None)
test_question = question.Question(test_timer)


# TODO: speed this up!
def test_daily_double_debug_flag():
    for q in range(10):
        dd_question = question.Question(test_timer, daily_double_debug=1)
        assert dd_question.daily_double == True


def test_get_value():
    '''
    we want to make sure that it's a valid Jeopardy point value,
    so it has to be in an increment of $100
    '''
    value_no_dollar_sign = test_question.get_value()[1:]
    assert int(value_no_dollar_sign) % 100 == 0

@pytest.mark.parametrize("test_text, expected_output", [
 # test working link
 ('''
 This patron saint of Lourdes'
 <a href="http://www.j-archive.com/media/2004-11-17_DJ_21.jpg"
 target="_blank">body</a>
 has remained unchanged in its glass display case since her death in 1879
 ''',
 ['This patron saint of Lourdes\' body has remained unchanged in its glass\
 display case since her death in 1879',
 'http://www.j-archive.com/media/2004-11-17_DJ_21.jpg']),

 # test 404 link
 ('''
 <a href="http://www.j-archive.com/media/2010-06-15_DJ_20.jpg" \
 target="_blank">What</a> the ant had in song
 ''',
 'What the ant had in song'),

 ('wrongtext  <a href="thisisntavalidlink"</a>  morewrongtext', 'wrongtext morewrongtext'),

 ('This is the first king of Poland', 'This is the first king of Poland'),

 # spacing looks ugly, but we need it so the test doesn't have extra spaces
 ('<a href="http://www.j-archive.com/media/2007-12-13_DJ_28.jpg" \
 target="_blank">Jon of the Clue Crew holds a purple gem in a pair of tweezers.</a> \
  It has more iron oxide than any other variety of quartz, which is believed to \
  account for its rich \
  <a href="http://www.j-archive.com/media/2007-12-13_DJ_28a.jpg" target="_blank">\
  color</a>', ['Jon of the Clue Crew holds a purple gem in a pair of tweezers.\
 It has more iron oxide than any other variety of quartz,\
 which is believed to account for its rich color',\
  "http://www.j-archive.com/media/2007-12-13_DJ_28.jpg",\
  "http://www.j-archive.com/media/2007-12-13_DJ_28a.jpg"])
])
def test_separate_html(test_text, expected_output):
    assert test_question.separate_html(test_text) == expected_output

@pytest.mark.parametrize("test_value, expected_value", [
 ('$100', False),
 ('$5578', True),
 (200, False),
 ('$201', True),
 (10239, True),
 (1, True),
 (-1, True),
 (0, True),
 ('0', True),
 ('$0', True)
])
def test_is_daily_double(test_value, expected_value):
    assert test_question.is_daily_double(test_value) == expected_value


def test_filter_questions():
    # set up
    test_json = open('./tests/test_files/test_questions.json').read()
    test_question_list = json.loads(test_json)

    # act
    dd_filter = test_question.filter_questions(test_question_list, daily_double=1)
    history_filter = test_question.filter_questions(test_question_list, banned_categories='history')
    science_filter = test_question.filter_questions(test_question_list, banned_categories=['science', 'biology', 'chemistry'])
    heard_seen_here_filter = test_question.filter_questions(
    test_question_list,
    banned_phrases=['heard here', 'seen here']
    )
    # tests filtering both, as we do when we init a Question instance
    # pdb.set_trace()
    category_and_phrase_filter = test_question.filter_questions(
    test_question_list,
    banned_categories='missing this category',
    banned_phrases=['heard here', 'seen here'],
    )

    # assert
    for c in dd_filter: assert test_question.is_daily_double(c['value'])
    for c in history_filter: assert c['category'] != 'HISTORY'
    for c in science_filter: assert c['category'] != 'SCIENCE'
    for q in heard_seen_here_filter: assert 'heard here' not in q['question']\
    and 'seen here' not in q['question']
    for q in category_and_phrase_filter: \
    assert 'heard here' not in q['question'] \
    and 'seen here' not in q['question'] \
    and q['category'] != 'missing this category'


@pytest.mark.parametrize("test_value, expected_value", [
 ('$2,500', 2500),
 ('asjdjasdj', 0),
 (0, 0),
 (-1, 0),
 (-888, 0),
 ('-$4,001', 0),
 (None, 0)
])
def test_convert_value_to_int(test_value, expected_value):
    assert test_question.convert_value_to_int(test_value) == expected_value


def test_get_questions_from_random_category():
    test_category_group = test_question.get_questions_from_random_category()
    test_category = test_category_group[0].category
    for q in test_category_group:
        assert q.category == test_category

