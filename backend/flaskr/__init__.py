import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


# Helper function to paginate questions
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    items = [item.format() for item in selection]
    current_items = items[start:end]

    return current_items


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow '*' for origins.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    #CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        # show all categories
        selection = Category.query.all()
        result = [item.format() for item in selection]

        if len(result) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': result,
            'total_categories': len(Category.query.all())
        })

    @app.route('/questions')
    def get_questions():
        # show all questions
        selection = Question.query.order_by(Question.id).all()
        questions = [item.format() for item in selection]
        page = request.args.get('page')

        selection_categories = Category.query.order_by(Category.id).all()
        categories = [item.format() for item in selection_categories]

        if page:
            paged_result = paginate_questions(request, selection)
        else:
            paged_result = questions

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': paged_result,
            'categories': categories,
            'total_questions': len(Question.query.all())
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(selection)
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            body = request.get_json()

            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_category = body.get('category', None)
            new_difficulty = body.get('difficulty', None)

            question = Question(question=new_question,
                                answer=new_answer,
                                category=new_category,
                                difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by('id').all()
            current_questions = paginate_questions(request, selection)

            selection_categories = Category.query.order_by(Category.id).all()

            all_categories = []
            for category in selection_categories:
                all_categories.append(category.type)
            # categories = [q.type for q in selection_categories]

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'categories': all_categories,
                'total_questions': len(selection)
            })

        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm', None)

            selection = Question.query.filter(
                Question.question.ilike('%' + search_term + '%')).all()

            results = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': results,
                'total_questions': len(results)
            })

        except:
            abort(404)

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        try:
            category = Category.query.filter(Category.id == category_id).all()

            if category is None:
                abort(404)

            selection = Question.query.order_by(
                Question.id).filter(Question.category == category_id).all()
            questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(questions),
                'current_category': category_id
            })

        except:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            quiz_category = body.get('quiz_category', None).get('id', None)
            previous_questions = body.get('previous_questions', None)

            if quiz_category == 0:
                selection = Question.query.order_by(Question.id).all()
            else:
                selection = Question.query.order_by(Question.id).filter(
                    Question.category == str(int(quiz_category))).all()

            questions = [question.format() for question in selection]
            available_questions = [
                question for question in questions
                if question.get('id', None) not in previous_questions
            ]

            if len(available_questions) != 0:
                question = available_questions.pop(
                    random.randrange(len(available_questions)))
                previous_questions.append(question.get('id', None))
            else:
                question = None

            return jsonify({
                'success': True,
                'question': question,
                'previous_questions': previous_questions
            })

        except Exception as e:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "not found"
        }), 404

    @app.errorhandler(422)
    def not_processable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''