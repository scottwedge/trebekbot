import pytest
import host
import question
import db
import slackclient
from re import findall
from os import remove
from main import slack_token

# set up test objects
sc = slackclient.SlackClient(slack_token)
test_question = question.Question()
test_host = host.Host(sc)
test_db = db.db('test.db')

# fixture for tearing down test database completely
@pytest.fixture
def db_after():
    yield db_after
    test_db.drop_table_users(test_db.connection)

# fixture for cleaning out test users from database (but leaving table present)
@pytest.fixture
def scrub_test_users():
    yield scrub_test_users
    test_db.connection.execute(
    '''
    DELETE FROM USERS
    '''
    )

# set up fixture to populate test db with a range of scorers
@pytest.fixture
def populate_db():
    test_users = ['Bob', 'Jim', 'Carol', 'Eve', 'Morp']
    test_score = 101
    # ensure that we have a varied list of scorers
    for user in test_users:
        test_db.add_user_to_db(test_db.connection, user)
        test_db.update_score(test_db.connection, user, test_score)
        test_score += 100
    # check to make sure negative numbers work too
    test_db.connection.execute(
    '''
    UPDATE USERS SET SCORE = ? WHERE NAME = ?
    ''',
    (-156, 'Eve')
    )
    test_db.connection.execute(
    '''
    UPDATE USERS SET CHAMPION_SCORE = ? WHERE NAME = ?
    ''',
    (5000, 'Morp')
    )

# tests question constructor
def test_question_constructor():
    assert type(test_question.answer) == str
    assert type(test_question.category) == str
    assert type(test_question.daily_double) == bool
    assert type(test_question.text) == str
    assert type(test_question.value) == int
    assert type(test_question.date) == str

def test_get_value():
    '''
    we want to make sure that it's a valid Jeopardy point value,
    so it has to be in an increment of $100
    '''
    value_no_dollar_sign = test_question.get_value()[2:]
    assert int(value_no_dollar_sign) % 100 == 0

@pytest.mark.parametrize("test_text, expected_output", [
 ('''This patron saint of Lourdes'
 <a href="http://www.j-archive.com/media/2004-11-17_DJ_21.jpg"
 target="_blank">body</a>
 has remained unchanged in its glass display case since her death in 1879')''',
 ('This patron saint of Lourdes has remained unchanged in its glass display \
 case since her death in 1879',
 'http://www.j-archive.com/media/2004-11-17_DJ_21.jpg')),

 # I'm ok with ignoring the 'What', this just seems like a badly parsed question
 ('''<a href="http://www.j-archive.com/media/2010-06-15_DJ_20.jpg" \
 target="_blank">What</a> the ant had in song''',
 'the ant had in song'),

 ('wrongtext  <a href="thisisntavalidlink"</a>  morewrongtext', 'wrongtext  morewrongtext'),

 ('<a href="http://www.j-archive.com/media/2007-12-13_DJ_28.jpg" \
 target="_blank">Jon of the Clue Crew holds a purple gem in a pair of tweezers.</a>) \
  It has more iron oxide than any other variety of quartz, which is believed to \
  account for its rich \
  <a href="http://www.j-archive.com/media/2007-12-13_DJ_28a.jpg" target="_blank">\
  color</a>', ('It has more iron oxide than any other variety of quartz, which is believed to \
  account for its rich color', "http://www.j-archive.com/media/2007-12-13_DJ_28a.jpg"))
])
def test_separate_html(test_text, expected_output):
    assert test_question.separate_html(test_text) == expected_output

@pytest.mark.parametrize("test_output, expected_value", [
 ([{'source_team': 'T0LR9NXQQ', 'team': 'T0LR9NXQQ', 'text':
 'aw, he restarted', 'type': 'message', 'ts': '1497097067.238474',
 'user': 'U1UU5ARJ6', 'channel': 'C5LMQHV5W'}], None),
 ([{'source_team': 'T0LR9NXQQ', 'team': 'T0LR9NXQQ', 'text':
 '..wager 500', 'type': 'message', 'ts': '1497097067.238474',
 'user': 'U1UU5ARJ6', 'channel': 'C5LMQHV5W'}], (500, 'bertrand_hustle')),
 ([{'source_team': 'T0LR9NXQQ', 'team': 'T0LR9NXQQ', 'text':
 '..wager bees', 'type': 'message', 'ts': '1497097067.238474',
 'user': 'U1UU5ARJ6', 'channel': 'C5LMQHV5W'}], None),
 ([{'source_team': 'T0LR9NXQQ', 'team': 'T0LR9NXQQ', 'text':
  '..wager 0', 'type': 'message', 'ts': '1497097067.238474',
  'user': 'U1UU5ARJ6', 'channel': 'C5LMQHV5W'}], None)
])
def test_get_wager(test_output, expected_value):
    assert test_host.get_wager(test_output) == expected_value

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
    test_question_list = [{"category": "HISTORY",
    "air_date": "2004-12-31",
    "question": "'For the last 8 years of his life, Galileo was under house\
     arrest for espousing this man's theory, seen here'",
    "value": "$200",
    "answer": "Copernicus",
    "round": "Jeopardy!",
    "show_number": 4680},
    {"category": "SCIENCE",
    "air_date": "2004-12-31",
    "question": "'For the last 8 years of his life, Galileo was under house\
     arrest for espousing this man's theory, heard here'",
    "value": "$201",
    "answer": "Copernicus",
    "round": "Jeopardy!",
    "show_number": 4680},
    {"category": "BIOLOGY",
    "air_date": "2004-12-31",
    "question": "'For the last 8 years of his life, Galileo was under house\
     arrest for espousing this man's theory'",
    "value": "$0",
    "answer": "Copernicus",
    "round": "Jeopardy!",
    "show_number": 4680},
    {"category": "BIOLOGY",
    "air_date": "2004-12-31",
    "question": "'Heard here, for the last 8 years of his life, Galileo was \
    under house arrest for espousing this man's theory'",
    "value": "$0",
    "answer": "Copernicus",
    "round": "Jeopardy!",
    "show_number": 4680}]

    # act
    dd_filter = test_question.filter_questions(test_question_list, daily_double=1)
    history_filter = test_question.filter_questions(test_question_list, banned_categories='history')
    science_filter = test_question.filter_questions(test_question_list, banned_categories=['science', 'biology', 'chemistry'])
    heard_seen_here_filter = test_question.filter_questions(test_question_list, banned_phrases=['heard here', 'seen here'])

    # assert
    for c in dd_filter: assert test_question.is_daily_double(c['value'])
    for c in history_filter: assert c['category'] != 'HISTORY'
    assert len(science_filter) == 1 and science_filter[0]['category'] not in ['science', 'biology', 'chemistry']
    assert len(heard_seen_here_filter) == 1
    for x in ['heard here', 'seen here']:
        assert x not in heard_seen_here_filter[0]['question']

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

@pytest.mark.parametrize("test_value, expected_value", [
 # we add an extra space because this is how we get the answers from slack
 (' Hall & Oates', 'hall oates'),
 (' Hall and Oates', 'hall oates'),
 (' Androgynous', 'androgynous'),
 (' Hall & Oates\' Oats and Halls', 'hall oates oats halls'),
 (' "The Little Rascals"', 'the little rascals')
])
def test_strip_answer(test_value, expected_value):
    assert test_host.strip_answer(test_value) == expected_value

@pytest.mark.parametrize("given_answer, expected_answer, expected_value", [
 ('Bath', 'Borth', False),
 ('Bath', 'beth', False),
 (600, 'Borth', False),
 (None, 'Borth', False),
 ('mary queen of scotts','Mary, Queen of Scots', True),
 ('','Mary, Queen of Scots', False),
 ('MAAAARYYYY QUEEN OF SCOOOOOOTTSSS','Mary, Queen of Scots', False),
 ('borp', 'Henry James', False),
 ('bagpipe', 'a bagpipe', True),
 ('amber alert', 'an Amber alert', True),
 ('infintesimal', 'infinitesimal', True),
 ('infiniitesimal', 'infinitesimal', True),
 ('the good Samaritan', 'The Good Samaritan', True),
 ('it’s a wonderful life', 'It\'s A Wonderful Life', True),
 ('Hall and Oates', 'Hall & Oates', True),
 ('b', 'the Boston Massacre', False),
 ('omlette', 'Denver omelette', 'close'),
 ('The Great Star of Bethlehem', 'The Star of Bethelhem', 'close'),
 ('lawn', 'The Great Lawn', 'close'),
 ('bechamel', 'béchamel', True),
 ('queen elizabeth ii', 'Elizabeth II', 'close'),
 ('issac newton', 'Newton', 'close'),
 ('dow jones', '(the) Dow (Jones)', True),
 ('91', '21', False),
 ('Red and Green', 'Green and Red', True),
 ('Blue or green', 'Green', True),
 ('poker', 'a poker face', 'close'),
 ('the gay 90\'s', 'The Gay \'90s', True),
 ('REM', 'R.E.M.', True),
 ('hard days night', '"A Hard Day\'s Night"', True),
 ('HG Wells', '(H.G.) Wells', True),
 ('cat\'s in the cradle', 'Cats In The Cradle', True),
 ('Zermelo Frankel set theory', 'Zermelo-Frankel Set Theory', True),
 ('00', '00', True)
])
def test_fuzz_answer(given_answer, expected_answer, expected_value):
    assert test_host.fuzz_answer(given_answer, expected_answer) == expected_value

# DATABASE TESTS

# TODO: rewrite database tests using Mock
# TODO: add bad values in here e.g. ' ', 0
def test_add_user_to_db():
    # do this twice to ensure that we're adhering to the UNIQUE constraint
    test_db.add_user_to_db(test_db.connection, 'Bob')
    test_db.add_user_to_db(test_db.connection, 'Bob')
    test_query = test_db.connection.execute(
    '''
    SELECT * FROM USERS WHERE NAME = ?
    ''',
    ('Bob',)
    )
    query_results = test_query.fetchall()
    print(query_results)
    check_results = findall(r'Bob', str(query_results))
    # asserts both that Bob was added and that he was only added once
    assert len(check_results) == 1

@pytest.mark.parametrize("user, value_change, expected_result", [
 ('LaVar', '0', 0),
 ('LaVar', '-200', -200),
 ('LaVar', '-200', -400),
 ('LaVar', '500', 100),
 ('Stemp', 'Invalid Value', 0),
 ('boop', '-9000', -9000),
 ('boop', '-500', -9500),
 # this makes sense, if we get a non-int it should do nothing
 ('LaVar', 'ants', 100)
])
def test_update_score(user, value_change, expected_result):
    test_db.add_user_to_db(test_db.connection, user)
    test_db.update_score(test_db.connection, user, value_change)
    assert test_db.get_score(test_db.connection, user) == expected_result

def test_return_top_ten(populate_db, scrub_test_users):
    expected_list = [
    (8, 'Morp', 501, 5000, 0),
    (6, 'Carol', 301, 0, 0),
    (5, 'Jim', 201, 0, 0),
    (1, 'Bob', 101, 0, 0),
    (2, 'LaVar', 100, 0, 0),
    (3, 'Stemp', 0, 0, 0),
    (7, 'Eve', -156, 0, 0),
    (4, 'boop', -9500, 0, 0)
    ]
    assert test_db.return_top_ten(test_db.connection) == expected_list

def test_get_champion(populate_db, scrub_test_users):
    expected_champion_name = 'Morp'
    expected_champion_score = 501
    assert test_db.get_champion(test_db.connection) == \
    (expected_champion_name, expected_champion_score)

def test_get_last_nights_champion(populate_db, scrub_test_users):
    expected_champion_name = 'Morp'
    expected_champion_score = 5000
    assert test_db.get_last_nights_champion(test_db.connection) == \
    (expected_champion_name, expected_champion_score)

def test_set_champion(populate_db, scrub_test_users):
    test_db.set_champion(test_db.connection, 'Morp', 501)
    test_result = test_db.connection.execute(
    '''
    SELECT * FROM USERS WHERE CHAMPION = 1
    '''
    ).fetchone()
    assert (test_result[1], test_result[3]) == ('Morp', 501)

# TODO: test if user doesn't exist
def test_get_score(db_after):
    test_db.add_user_to_db(test_db.connection, 'Lucy')
    assert test_db.get_score(test_db.connection, 'Lucy') == 0
    test_db.connection.execute(
    '''
    UPDATE USERS SET SCORE = ? WHERE NAME = ?
    ''',
    (100, 'Lucy')
    )
    assert test_db.get_score(test_db.connection, 'Lucy') == 100

def test_wipe_scores(populate_db, db_after):
    test_db.wipe_scores(test_db.connection)
    # get scores
    test_scores = test_db.connection.execute(
    '''
    SELECT * FROM USERS ORDER BY SCORE DESC
    ''',
    ).fetchall()
    test_scores = [x[2] for x in test_scores]
    # this works because every score should be 0
    assert not any(test_scores)

def test_log_db(populate_db, db_after):
    test_db.log_db(test_db.db_file)
    test_backup_db = db.db('test_db.bak')
    assert test_db.get_champion(test_backup_db.connection) == ('Morp', '$501')
