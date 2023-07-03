import json
import os
import unittest

from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import Category, Question, setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        # TODO: Restore the original shape??
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        self.app = create_app(self.database_path)
        self.client = self.app.test_client

        # setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is tha name of this project?',
            'answer': 'Trivia API',
            'difficulty': 1,
            'category': 5
        }


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
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        # self.assertTrue(data['current_category'])

    # Test for possible error
    def test_404_error_paginating_questions_page_beyond_available(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    # Test for the endpoint to DELETE question using a question ID
    def test_delete_question(self):
        question_id = 9
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertTrue(data['total_questions'])

    # Test for possible error
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
        
        





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()