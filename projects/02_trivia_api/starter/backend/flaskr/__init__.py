import os
import random

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import Category, Question, setup_db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

# TODO: Restore the original shape??
# def create_app(test_config=None):
def create_app(db_URI="", test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if db_URI:
        setup_db(app, db_URI)
    else:
        setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response


    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def show_categories():
        categories = Category.query.order_by(Category.id).all()
        categories_list = [category.format() for category in categories]

        if len(categories_list) == 0:
            abort(404)

        try:
            # Makes the correct format of the dictionary as {'id': 'type'}
            categories_dict = {}
            for i in categories_list:
                categories_dict[str(i['id'])] = i['type']

            return jsonify({
                'success': True,
                'categories': categories_dict
            })
        except:
            abort(500)


    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions')
    def show_paginated_questions():
        # Calls the paginating function
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)

        try:
            categories = Category.query.order_by(Category.id).all()
            categories_list = [category.format() for category in categories]

            # Makes the correct format of the dictionary as {'id': 'type'}
            categories_dict = {}
            for i in categories_list:
                categories_dict[str(i['id'])] = i['type']

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions),
                'categories': categories_dict,
                'current_category': 1
            })
        except:
            abort(500)


    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        try:
            question.delete()

            questions = Question.query.all()
            return jsonify({
                'success': True,
                'deleted': question_id,
                'total_questions': len(questions)
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
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        search = body.get('searchTerm')

        question = body.get('question')
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        category = body.get('category')
        
        if search:
            try:
                questions = Question.query.order_by(Question.id).filter(
                    Question.question.ilike(f'%{search}%')
                )
                current_questions = paginate_questions(request, questions)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'found_questions': len(questions.all())
                })
            except:
               abort(422) 
        else:
            # To make sure all the fields are provided in the API request
            if question is None or answer is None or difficulty is None or category is None:
                abort(400)

            # To make sure all the fields are filled on the frontend
            if question == "" or answer == "":
                abort(400)
            try:
                new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
                new_question.insert()

                return jsonify({
                    'success': True,
                    'created':new_question.id,
                    'total_questions': len(Question.query.all())
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
    # Done in the previous endpoint


    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<category_id>/questions')
    def get_questions_by_category(category_id):
        questions = Question.query.order_by(Question.id).filter_by(category=category_id).all()
        if len(questions) == 0:
            abort(404)
            
        questions_list = paginate_questions(request, questions)
        
        return jsonify({
            'success': True,
            'questions': questions_list,
            'current_category': category_id,
            'total_questions': len(questions_list)
        })


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

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"
            }), 404)

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({
                "success": False,
                "error": 405,
                "message": "method not allowed"
            }), 405)

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({
                "success": False,
                "error": 422,
                "message": "unprocessable"
            }), 422)

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({
                "success": False,
                "error": 400,
                "message": "bad request"
            }), 404)

    @app.errorhandler(500)
    def unprocessable(error):
        return (
            jsonify({
                "success": False,
                "error": 500,
                "message": "internal server error"
            }), 500)

    return app

    