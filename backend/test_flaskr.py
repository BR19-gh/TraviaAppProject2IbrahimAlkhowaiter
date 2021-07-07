import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = "postgresql://student:student@localhost:5432/trivia_test"
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            'id': 24,
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 2,
            'category': 1,
        }

        

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

    def testRetrieveCategs(self):
        # GET Categories
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
        self.assertIsInstance(data['categories'], dict)

    def testRetrieveQues(self):
        
        # Test Retrieve Questions
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        # Status Code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


        # Categories
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
        self.assertIsInstance(data['categories'], dict)
        self.assertEqual(data['current_category'], None)


        # Questions
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 10)

        # Total Questions
        self.assertEqual(data['total_questions'], 19)

    def test404SentRequestingQuestionsAfterValidPage(self):
        
        # Test Questions After Valid Page
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def testCreateQuestion(self):
        
        # Create Question
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['created'], 24)

    def tesTdeleteQue(self):
        # Delete Question
        res = self.client().delete('/questions/24')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 24)

    def test404SendNotValidIdForDeleteQue(self):
        
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def testSearchQues(self):

        res = self.client().post(
            '/search',
            json={'searchTerm': 'Taj Mahal'}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['current_category'], None)

    def testSearchQuesWithoutResults(self):

        res = self.client().post(
            '/search',
            json={'searchTerm': 'aaaaa'}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['current_category'], None)

    def testGetQuesBYcategory(self):

        res = self.client().get('/categories/1/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['current_category'], 1)

    def testQuizzesWITHOUTCategoryAndWITHOUTallPreviousQues(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': '0',
                'type': 'All'
            }
        })
        data = json.loads(res.data)

        # Status Code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)

    def testQuizzesWithCategoryAndWITHOUTallPreviousQues(self):

        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)

    def testQuizzesWithCategoryAndwithSOMEpreviousQues(self):

        res = self.client().post('/quizzes', json={
            'previous_questions': [13, 14],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)

    def testQuizzesWithCategoryAndWithALLPreviousQues(self):

        res = self.client().post('/quizzes', json={
            'previous_questions': [13, 14, 15],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
