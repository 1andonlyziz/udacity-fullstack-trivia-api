import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):

        # get response and load data
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that total_questions and questions return data
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_request_beyond_valid_page(self):

        # send request with bad page data, load response
        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):

        # send get request to categories
        response = self.client().delete('/questions/1')

        deleted_question = Question.query.filter_by(id=1).one_or_none()
        # check if the request returns 200
        self.assertEqual(response.status_code, 200)
        # check if the question is equal to None
        self.assertEqual(deleted_question, None)

    def test_insert_question(self):
        question_dict = {
            "answer": "Tested Answer",
            "category": 3,
            "difficulty": 1,
            "id": 22,
            "question": "Tested Question"
        }

        # send post request to create a questions
        response = self.client().post('/questions', json=question_dict)
        data = json.loads(response.data)
        # check if the response returns status code 200
        self.assertEqual(response.status_code, 200)
        # check if the respone data will returns True
        self.assertEqual(data['success'], True)

    def test_422_if_question_creation_fails(self):

        # get number of questions before post
        questions_before = Question.query.all()

        # create new question without json data, then load response data
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        # get number of questions after post
        questions_after = Question.query.all()

        # check status code and success message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

        # check if questions_after and questions_before are equal
        self.assertTrue(len(questions_after) == len(questions_before))

    def test_get_questions_by_category(self):

        # send get request to get question by category
        response = self.client().get('/categories/1/questions')
        # load response data
        data = json.loads(response.data)

        # check if the response will return status code 200
        self.assertEqual(response.status_code, 200)
        # check if the response data will return true
        self.assertEqual(data['success'], True)

        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_400_if_questions_by_category_fails(self):

        # send request with category id 100
        response = self.client().get('/categories/100/questions')

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_search_questions(self):

        # send post request with search term
        response = self.client().post('/questions',
                                      json={'searchTerm': 'egyptians'})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that number of results = 1
        self.assertEqual(len(data['questions']), 1)

        # check that id of question in response is correct
        self.assertEqual(data['questions'][0]['id'], 23)

    def test_404_if_search_questions_fails(self):

        # send post request with search term that should fail
        response = self.client().post('/questions',
                                      json={'searchTerm': 'abcdefghijk'})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_quiz(self):

        # send post request with category and previous questions
        response = self.client().post('/quizzes',
                                      json={'previous_questions': [20, 21],
                                            'quiz_category': {'type': 'Science', 'id': '1'}})
        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that a question is returned
        self.assertTrue(data['question'])

        # check that the question returned is in correct category
        self.assertEqual(data['question']['category'], 1)

        # check that question returned is not on previous q list
        self.assertNotEqual(data['question']['id'], 20)
        self.assertNotEqual(data['question']['id'], 21)

    def test_play_quiz_fails(self):

        # send post request without json data
        response = self.client().post('/quizzes', json={})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
