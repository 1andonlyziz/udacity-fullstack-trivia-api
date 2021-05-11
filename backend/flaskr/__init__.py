import os
from flask import Flask, request, abort, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

questions_per_page = 10

# a method to limit search to question to 10 per page 
def paginate_questions(request,selection):

  page = request.args.get('page',1,type=int)
  start = (page - 1) * questions_per_page
  end = start + questions_per_page

  questions = [Question.format() for Question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  CORS(app,resources={r"/api/*": {"origins": "*"}}) # allow resource sharing in all domains ports etc.

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):

      response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Methods','GET,POST,PATCH,DELTE,OPTIONS')
      return response
      
  '''
  @TODO: -- done
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories',methods=['GET'])
  def get_all_categories():
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = {category.id: category.type for category in categories}
    
    return jsonify({
      'success':True,
      'categories':formatted_categories
    })

  '''
  @TODO: -- done
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions',methods=['GET'])
  def get_questions():
    
    # search in db for all avaiable questions and order it by id
    selection = Question.query.order_by(Question.id).all()
    # limit the questions to 10 per each page
    current_questions = paginate_questions(request,selection)
    # search for all categories in db and order it by id
    categories = Category.query.order_by(Category.id).all()

    if len(current_questions) == 0:
      abort(404)

    # return json response
    return jsonify({
      'success':True,
      'questions':current_questions,
      'total_questions':len(Question.query.all()),
      'categories':{category.id: category.type for category in categories}
    })

    
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:id>',methods=['DELETE'])
  def delete_question(id):

    try :
      # search for the question you want to delete in DB
      question = Question.query.filter_by(id=id).one_or_none()
      
      # check if the question is there or not
      if question is None :
        abort(404)
      
      #perform deletion
      question.delete()

      return jsonify({
        'success':True,
        'deleted':id
      })
    
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def add_question(): 

    # get the data from json
    body = request.get_json()

    #check json body 
    if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
      abort(422)

    # fetch data from front end
    new_question = body.get('question')
    new_answer = body.get('answer')
    new_difficulty = body.get('difficulty')
    new_category = body.get('category')

    # add the question
    try:
      added_question = Question(question=new_question,answer=new_answer,difficulty=new_difficulty,category=new_category)
      added_question.insert()

    # return json response
      return jsonify({
        'success':True,
        'created':added_question.id
      })

    except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  
  @app.route('/questions/search',methods=['POST'])
  def search_question():

    # get raw data
    body = request.get_json()
    search_term = body.get('searchTerm')
    
    #check the searchTerm from front is available in DB
    if search_term:
      search_results=Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

    # return json reply
      return jsonify({
        'success':True,
        'questions':[question.format() for question in search_results],
        'total_questions':len(Question.query.all())
      })
      
    abort(404)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions',methods=['GET'])
  def get_question_by_category(category_id):


    try:
      # fetch all the categories in front from db
      questions = Question.query.filter(Question.category == str(category_id)).all()

      # return json response
      return jsonify({
        'sucess':True,
        'questions':[question.format() for question in questions],
        'total_questions':len(questions)
      })
    except:
      abort(404)


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
  @app.route('/quizzes',methods=['POST'])
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
          available_questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_((previous_questions))).all()

      new_question = available_questions[random.randrange(
          0, len(available_questions))].format() if len(available_questions) > 0 else None

      return jsonify({
          'success': True,
          'question': new_question
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  # ---------- Error handling 
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'sucess':False,
      'error':404,
      'message':'resource not found'
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

    