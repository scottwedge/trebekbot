import pytest
import host


def test_get_question():
    test_question = host.get_question()
    print(test_question.value)
    assert type(test_question) == host.Question
    assert type(test_question.category) is str
    assert type(test_question.value) is int
    assert type(test_question.text) is str

def test_get_value():
    test_question = host.get_question()
    '''
    we want to make sure that it's a valid Jeopardy point value,
    so it has to be in an increment of $100
    '''
    value_no_dollar_sign = test_question.get_value()[2:]
    assert int(value_no_dollar_sign) % 100 == 0

def test_is_daily_double():
    test_values = ['$100', '$5578', 200, 10239, 1, -1, 0]
    # test_question = host.Question()
    '''
    assert test_question.is_daily_double(test_values[0]) is False
    assert test_question.is_daily_double(test_values[1]) is True
    assert test_question.is_daily_double(test_values[2]) is False
    assert test_question.is_daily_double(test_values[3]) is True
    assert test_question.is_daily_double(test_values[4]) is False
    assert test_question.is_daily_double(test_values[5]) == 'Invalid Value'
    assert test_question.is_daily_double(test_values[6]) == 'Invalid Value'
    '''

    assert host.Question.is_daily_double(test_values[0]) is False
    assert host.Question.is_daily_double(test_values[1]) is True
    assert host.Question.is_daily_double(test_values[2]) is False
    assert host.Question.is_daily_double(test_values[3]) is True
    assert host.Question.is_daily_double(test_values[4]) is False
    assert host.Question.is_daily_double(test_values[5]) == 'Invalid Value'
    assert host.Question.is_daily_double(test_values[6]) == 'Invalid Value'

@pytest.mark.parametrize("test_value, expected_value", [
 ('$2,500', 2500),
 ('asjdjasdj', 'Invalid Value'),
 (0, 'Invalid Value'),
 (-1, 'Invalid Value'),
 (-888, 'Invalid Value'),
 ('-$4,001', 'Invalid Value')
])
def test_convert_value_to_int(test_value, expected_value):
    assert host.Question.convert_value_to_int(test_value) == expected_value
