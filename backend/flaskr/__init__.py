import os
from flask import Flask, request, abort, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

questions_per_page = 10

# a method to limit search to question to 10 per page


def paginate_questions(request, selection):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * questions_per_page
    end = start + questions_per_page

    questions = [Question.format() for Question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # allow resource sharing in all domains ports etc.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):

        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,PATCH,DELTE,OPTIONS')

        return response

    @app.route('/categories', methods=['GET'])
    def get_all_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {
            category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():

        # search in db for all avaiable questions and order it by id
        selection = Question.query.order_by(Question.id).all()
        # limit the questions to 10 per each page
        current_questions = paginate_questions(request, selection)
        # search for all categories in db and order it by id
        categories = Category.query.order_by(Category.id).all()

        if len(current_questions) == 0:
            abort(404)

        # return json response
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': {category.id: category.type for category in categories}
        })

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):

        try:
            # search for the question you want to delete in DB
            question = Question.query.filter_by(id=id).one_or_none()

            # check if the question is there or not
            if question is None:
                abort(404)

            # perform deletion
            question.delete()

            return jsonify({
                'success': True,
                'deleted': id
            })

        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def add_question():

        # get the data from json
        body = request.get_json()

        # check json body
        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(422)

        # fetch data from front end
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        # add the question
        try:
            added_question = Question(
                question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
            added_question.insert()

        # return json response
            return jsonify({
                'success': True,
                'created': added_question.id
            })

        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():

        # get raw data
        body = request.get_json()
        search_term = body.get('searchTerm')

        # check the searchTerm from front is available in DB
        if search_term:
            search_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

        # return json reply
            return jsonify({
                'success': True,
                'questions': [question.format() for question in search_results],
                'total_questions': len(Question.query.all())
            })

        abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_by_category(category_id):

        try:
            # fetch all the categories in front from db
            questions = Question.query.filter(
                Question.category == str(category_id)).all()

            # return json response
            return jsonify({
                'sucess': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions)
            })
        except:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def start_quiz():
        try:
            # get json data from front
            body = request.get_json()

            # check whether the body containts quiz_category and previous_question
            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

            # fetch data from front
            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if category['type'] == 'click':
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                available_questions = Question.query.filter_by(category=category['id']).filter(
                    Question.id.notin_((previous_questions))).all()

            new_question = available_questions[random.randrange(
                0, len(available_questions))].format() if len(available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })

        except:
            abort(422)

    # ---------- Error handling
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'sucess': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "bad request"
        }), 400

    return app
