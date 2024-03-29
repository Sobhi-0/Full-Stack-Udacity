import json
import os

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from sqlalchemy import exc

from .auth.auth import AuthError, requires_auth
from .database.models import Drink, db_drop_and_create_all, setup_db

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''

# with app.app_context():
#     db_drop_and_create_all()

# ROUTES
'''
TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    # if no drinks found then raises 404 error
    if len(drinks) == 0:
        print("ERROR ==> No drinks were found!")
        abort(404)

    drinks_list = [drink.short() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": drinks_list
    })


'''
TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    # the function needs to have a positional argumnet
    # because the requires_auth decorater returns the payload
    drinks = Drink.query.all()

    # if no drinks found then raises 404 error
    if len(drinks) == 0:
        print("ERROR ==> No drinks were found!")
        abort(404)

    drinks_list = [drink.long() for drink in drinks]
    # print("JWT ==>", jwt)

    return jsonify({
        "success": True,
        "drinks": drinks_list
    })


'''
TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(jwt):
    body = request.get_json()

    try:
        # gets the nessecary items from the request
        title = body.get('title')
        recipe = body.get('recipe')
        # if title or recipe not provided raises value error
        if title is None or recipe is None:
            raise ValueError
    except:
        print("ERROR ==> Must provide title and recipe to add a new drink")
        abort(400)

    # makes sure that the new drink doesn't already exist
    drinks = Drink.query.all()
    for drink in drinks:
        if drink.title == title:
            print("ERROR ==> Can't have duplicate layer names")
            abort(409)

    try:
        # actually adding to the database
        new_drink = Drink(title=str(title), recipe=json.dumps(recipe))
        new_drink.insert()
    except:
        abort(500)

    # adding the drink to a list to make sure the return is in the correct json format
    new_drink_list = [new_drink.long()]

    return jsonify({
        "success": True,
        "drinks": new_drink_list
    })


'''
TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, id):
    drink = Drink.query.get(id)

    # if the id doesn't exist it raises not found error
    if drink is None:
        abort(404)

    # gets the nessecary items from the request
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')

    # if an error occured it raises internal server error
    try:
        if title is not None:
            drink.title = title
        if recipe is not None:
            drink.recipe = json.dumps(recipe)

        drink.update()
    except:
        abort(500)

    updated_drink_list = [drink.long()]

    return jsonify({
        "success": True,
        "drinks": updated_drink_list
    })


'''
TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id):
    drink = Drink.query.get(id)

    # if the id doesn't exist it raises not found error
    if drink is None:
        abort(404)

    drink.delete()

    # checks if the drink was actually deleted from the database
    drink = Drink.query.get(id)
    if drink is not None:
        abort(500)

    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Drink not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400


@app.errorhandler(409)
def conflict(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "Conflict"
    }), 409


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500


@app.errorhandler(AuthError)
def handle_auth_error(error):
    return jsonify({
        'success': False,
        'error': error.error,
        'status_code': error.status_code
    }), error.status_code


'''
TODO implement error handler for AuthError
    error handler should conform to general task above
'''
# To handle each Auth
if __name__ == "__main__":
    app.debug = True
    app.run()
