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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    def test_fetch_question(self):

        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)

    def test_fetch_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
    
    def test_delete_question(self):

        response = self.client().delete('/questions/1')
        data = json.loads(response.data)

        deleted_question = Question.query.filter_by(id=1).one_or_none()

        self.assertEqual(response.status_code,200)
        self.assertEqual(deleted_question,None)
    
    def test_insert_question(self):
        question_dict = {
            "answer": "Simple Answer", 
            "category": 5, 
            "difficulty": 4, 
            "id": 99, 
            "question": "Simple Question"
        }
        response = self.client().post('/questions',json=question_dict)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()