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
        self.database_path = "postgres://{}/{}".format('localhost:5432',
                                                       self.database_name)
        setup_db(self.app, self.database_path)

        self.create_question = {
            'question': 'Question',
            'answer': 'Answer',
            'category': 1,
            'difficulty': 1
        }

        self.incomplete_question = {'question': 'Test_Q3', 'answer': 'Test_A3'}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_get_questions_invalid_page(self):
        res = self.client().get('questions/?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'not found')

    def test_delete_question(self):
        response = self.client().get('/questions')

        questions = json.loads(response.data)
        question_id = questions['questions'][0]['id']

        response = self.client().delete('/questions/' + str(question_id))

        reply = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reply['success'], True)
        self.assertEqual(reply['deleted'], question_id)

    def test_404_delete_questions(self):
        response = self.client().delete('/questions/99999999')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.create_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_422_create_new_questions(self):
        response = self.client().post('/questions')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'unprocessable')

    def test_search_for_questions(self):
        search = {'searchTerm': 'title'}
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIn('questions', data)
        self.assertIn('total_questions', data)

    def test_404_search_for_questions(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'not found')

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn('questions', data)
        self.assertIn('total_questions', data)

    def test_post_quizzes(self):
        quiz = {
            'previous_questions': [100],
            'quiz_category': {
                'type': 'test',
                'id': 0
            }
        }
        response = self.client().post('/quizzes', json=quiz)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data['question']))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()