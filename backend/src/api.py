import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from werkzeug.datastructures import ImmutableMultiDict
from flask_cors import CORS
from .auth.auth import AuthError, requires_auth
from .database.models import db_drop_and_create_all, setup_db, Drink


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES


def index():
    return jsonify({
        'success': True,
        'message': 'hello-coffee'})


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'], endpoint='get_drinks')
def get_drinks():

    allDrinks = Drink.query.order_by(Drink.id).all()
    try:
        return json.dumps({
            'success': True,
            'drinks': [drink.short() for drink in allDrinks]
        }), 200
    except Exception:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'], endpoint='drinks_detail')
@requires_auth('get:drinks-detail')
def get_drink_details(jwt):
    allDrinks = [drink.long() for drink in Drink.query.all()]
    try:
        return json.dumps({
            'success': True,
            'drinks': allDrinks
        }), 200
    except Exception:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'], endpoint='post_drink')
@requires_auth('post:drinks')
def post_drinks(jwt):
    data = request.get_json()

    if 'title' and 'recipe' not in data:
        abort(422)

    drink = Drink(title=data['title'], recipe=json.dumps(data['recipe']))
    try:
        drink.insert()
        return json.dumps({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'], endpoint='patch_drink')
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    try:
        drink = Drink.query.get(id)

        if drink:
            data = request.get_json()
            if 'title' in data:
                drink.title = data['title']
            if 'recipe' in data:
                drink.recipe = json.dumps(data['recipe'])
            drink.update()
            return json.dumps({
                'success': True,
                'drinks': [drink.long()]
            }), 200
        else:
            return json.dumps({
                'success':
                False,
                'error':
                'Drink #' + id + ' not found to be edited'
            }), 404
    except Exception:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'], endpoint='delete_drink')
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    try:
        drink = Drink.query.get(id)
        if drink:
            drink.delete()

            return json.dumps({
                'success': True,
                'delete': drink.id
            }), 200

        else:
            return json.dumps({
                'success': False,
                'error': 'Drink: ' + id + ' not found'
            }), 404
    except Exception:
        return json.dumps({
            'success': False,
            'error': "Error occurred"
        }), 500


'''
Tesintg Auth0
'''


@app.route('/login-results', methods=['GET'])
def login_results():

    return (
        jsonify({
            'message': 'Successfully Logged In'
        })
    )


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "Unprocessable"
                    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(400)
def unprocessable(error):

    return jsonify({
        "success": False,
        "error": 400,
        "message": "Check the body request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):

    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401


'''
@TODO implement error handler for 404
error handler should conform to general task above
'''


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def process_AuthError(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
