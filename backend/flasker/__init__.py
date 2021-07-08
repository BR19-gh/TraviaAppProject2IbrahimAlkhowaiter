from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from models import setup_db, Question, Category


CATEGORY_ALL = '0'
QUESTIONS_PER_PAGE = 10



def getIdsFromQues(ques, pre_ids):
    '''
    this function will create a formatted list of current questions,
    then it will compare both lists then return list of IDs
    '''
    ques_formatted = [q.format() for q in ques]
    cur_ids = [q.get('id') for q in ques_formatted]

    ids = list(set(cur_ids).difference(pre_ids))

    return ids


def create_app(test_config=None):
    '''
    config
    '''
    app = Flask(__name__)
    setup_db(app)
    CORS(app)


    @app.after_request
    def after_request(res):
        '''
        @TODO: Use the after_request decorator to set Access-Control-Allow (headers)
        '''
        
        res.headers.add(
          'Access-Control-Allow-Headers', 'Content-Type, Authorization, true'
        )
        res.headers.add(
          'Access-Control-Allow-Methods', 'GET,PUT,POST, DELETE, OPTIONS'
        )

        return res

    @app.route('/categories', methods=['GET'])
    def restoreCategs():
                '''
                @TODO: 
                Create an endpoint to handle GET requests 
                for all available categories.
                '''
                try:
                    categs = Category.query.order_by(Category.id).all()

                    return jsonify({
                    'success': True,
                    'categories': {
                        categ.id: categ.type for categ in categs
                    }
                    })
                except Exception:
                    abort(422)

    @app.route('/questions', methods=['GET'])
    def restoreQues():
        '''
        @TODO: 
        Create an endpoint to handle GET requests for questions, 
        including pagination (every 10 questions). 
        This endpoint should return a list of questions, 
        number of total questions, current category, categories. 
        '''
        try:
                page = req.args.get('page', 1, type=int)

                # categories
                categs = Category.query.order_by(Category.id).all()
                categs_formatted = {
                categ.id: categ.type for categ in categs
                }

                # questions
                ques = Question.query \
                    .order_by(Question.id) \
                    .paginate(page=page, per_page=QUESTIONS_PER_PAGE)

                ques_formatted = [
                que.format() for que in ques.items
                ]

                if len(ques_formatted) == 0:
                    abort(404)
                else:
                    return jsonify({
                    'success': True,
                    'questions': ques_formatted,
                    'total_questions': ques.total,
                    'categories': categs_formatted,
                    'current_category': None,
                    })
        except Exception as e:
                if '422' in str(e):
                    abort(422)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def deleteQues(question_id):
            '''
            @TODO: 
            Create an endpoint to DELETE question using a question ID. 

            TEST: When you click the trash icon next to a question, the question will be removed.
            This removal will persist in the database and when you refresh the page. 
            '''
            try:
                # question
                que = Question.query \
                .filter(Question.id == question_id) \
                .one_or_none()

                if que is None:
                    abort(404)

                que.delete()

                return jsonify({
                'success': True,
                'deleted': question_id,
                })
            except Exception as e:
                if '422' in str(e):
                    abort(422)

    @app.route('/questions', methods=['POST'])
    def createQues():
            '''
            @TODO: 
            Create an endpoint to POST a new question, 
            which will require the question and answer text, 
            category, and difficulty score.
            '''

            # Get Data
            body = req.get_json()
            que = body.get('question', None)
            answer = body.get('answer', None)
            difficulty = body.get('difficulty', None)
            categ = body.get('category', None)

            try:
                # Create Question
                que = Question(que=que,answer=answer,difficulty=difficulty,categ=categ)

                # Update Database
                que.insert()

                return jsonify({
                'success': True,
                'created': que.id,
                })
            except Exception:
                abort(422)

    @app.route('/search', methods=['POST'])
    def searchQues():
            '''
            @TODO: 
            Create a POST endpoint to get questions based on a search term. 
            It should return any questions for whom the search term 
            is a substring of the question. 
            '''

            # Get Data
            body = req.get_json()
            search = body.get('searchTerm', None)

            try:
                # Search Term
                ques = Question.query \
                .order_by(Question.id) \
                .filter(Question.que.ilike('%{}%'.format(search)))

                ques_formatted = [que.format() for que in ques]

                return jsonify({
                'success': True,
                'questions': ques_formatted,
                'total_questions': len(ques.all()),
                'current_category': None,
                })
            except Exception:
                abort(422)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def restoreQuesByCategs(categ_id):
                    '''
                    @TODO: 
                    Create a GET endpoint to get questions based on category. 
                    '''
                    try:
                        # page
                        page = req.args.get('page', 1, type=int)

                        # questions
                        ques = Question.query \
                            .order_by(Question.id) \
                            .filter(Question.categ == categ_id) \
                            .paginate(page=page, per_page=QUESTIONS_PER_PAGE)

                        ques_formatted = [
                        que.format() for que in ques.items
                        ]

                        if len(ques_formatted) == 0:
                            abort(404)
                        else:
                            return jsonify({
                            'success': True,
                            'questions': ques_formatted,
                            'total_questions': ques.total,
                            'current_category': categ_id
                            })
                    except Exception as e:
                        if '422' in str(e):
                            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def restoreQuizzes():
                '''
                @TODO: 
                Create a POST endpoint to get questions to play the quiz. 
                This endpoint should take category and previous question parameters 
                and return a random questions within the given category, 
                if provided, and that is not one of the previous questions. 
                '''

                try:
                    # Get Data
                    ques = None
                    body = req.get_json()
                    quiz_categ = body.get('quiz_category', None)
                    pre_ids = body.get('previous_questions', None)
                    categ_id = quiz_categ.get('id')

                    # Check Category
                    if categ_id == CATEGORY_ALL:
                        # Get all Questions
                        ques = Question.query.all()
                    else:
                        # Get Questions by Requested Category
                        ques = Question.query \
                            .filter(Question.categ == categ_id) \
                            .all()

                    # Get List of IDs
                    ids = get_ids_from_ques(ques, pre_ids)

                    if len(ids) == 0:
                        # If There are No IDs (Empty List), Do Not Return question
                        return jsonify({
                        'success': True,
                        'question': None
                        })
                    else:
                        # Choose Random ID
                        random_id = random.choice(ids)

                        # Get Question
                        que = Question.query.get(random_id)

                        return jsonify({
                        'success': True,
                        'question': que.format()
                        })

                except Exception:
                    abort(422)

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''


    @app.errorhandler(400)
    def badRequest(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def notFound(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(500)
    def internalServerError(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app
