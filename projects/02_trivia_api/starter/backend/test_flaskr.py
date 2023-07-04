import json
import os
import unittest

from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import Category, Question, setup_db

"""
IMPORTANT NOTE to the reviewer:
Beacuse setup_db was used more than once through the application and that was causing this error

RuntimeError: A 'SQLAlchemy' instance has already been registered on this Flask app

I adjusted the code so it works, please refer to this StackOverflow question for more
details on what changed and the error itself
https://stackoverflow.com/questions/75523569/runtimeerror-a-sqlalchemy-instance-has-already-been-registered-on-this-flask
"""


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        # TODO: Restore the original shape??
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        self.app = create_app(self.database_path)
        self.client = self.app.test_client

        # See the note to know why commented
        # setup_db(self.app, self.database_path)

        # Question to be added where needed in the tests
        self.new_question = {
            'question': 'What is tha name of this project?',
            'answer': 'Trivia API',
            'difficulty': 1,
            'category': 5
        }

        # See the note to know why commented
        # # binds the app to the current context
        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     # create all tables
        #     self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Test for nonexistent endpoints
    def test_404_nonexistent(self):
        res = self.client().get('/nonexistent')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # Test the endpoint to handle GET requests for all available categories
    def test_show_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        

    # Test the endpoint to handle GET requests for questions
    def test_show_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # Makes sure there is questions
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['current_category'])

    # Test for possible error
    def test_404_error_paginating_questions_page_beyond_available(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    # Test for the endpoint to DELETE question using a question ID
    def test_delete_question(self):
        question_id = 6
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        
        # Testing that it actaully got deleted from the database
        with self.app.app_context():
            question = Question.query.get(question_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # If it is None then it was deleted from the database
        self.assertEqual(question, None)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertTrue(data['total_questions'])

    # Test for deleting a question that doesn't exist
    def test_404_delete_nonexistent_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    # Test for endpoint to POST a new question
    def test_adding_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # Checking if it actaully got created on the database
        # if true then there is an id which means it was created
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'])

    # Test for possible error
    def test_405_adding_question_with_id_in_the_request(self):
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')


    # Test for POST endpoint to get questions based on a search term
    def test_search_questions_with_resault(self):
        res = self.client().post('/questions', json={'searchTerm': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['found_questions'])
    
    # Test for POST endpoint to get questions based on a search term
    # with no resaults
    def test_search_questions_without_resault(self):
        res = self.client().post('/questions', json={'searchTerm': 'SomethingUnknown'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['found_questions'], 0)


    # Test for POST endpoint to get questions based on category
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    # Test if the category doesn't exist when getting questions based on category
    def test_404_get_questions_by_not_available_category(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    # Test for POST endpoint to get questions to play the quiz
    # This tests when there is avaiable questions to be played 
    # in this test case there is only one question remaining which is 20
    # (based on the trivia_test database trivia.psql)
    # it should be the one that is returned by the API
    def test_quizzes_play_with_available_questions(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'type': 'Science', 'id': '1'}, 'previous_questions': [22, 21]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # Tests that there is a returned question
        self.assertTrue(data['random_question'])
        # Tests that the returned question was not shown before
        self.assertEqual(data['random_question']['id'], 20)
        # Tests that the previous_questions list is returned
        self.assertTrue(data['previous_questions'])

    # Test for POST endpoint to get questions to play the quiz
    # This tests when there is NO avaiable questions to be played 
    def test_quizzes_play_with_NO_available_questions(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'type': 'Science', 'id': '1'}, 'previous_questions': [20, 21, 22]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # Tests that the previous_questions list is returned with
        # all the displayed questions
        self.assertEqual(len(data['previous_questions']), 3)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()