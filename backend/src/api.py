from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from auth import requires_auth, AuthError
from database import setup_db, Drink, Recipe

def add_recipe(body, drink):
    recipes = body.get('recipe', None)
    if recipes is None:
        return jsonify({
            "success": False,
            "errors": "Invalid recipe"
        }), 400

    for recipe in recipes:
        if 'name' not in recipe or 'parts' not in recipe or 'color' not in recipe:
            return jsonify({
                "success": False,
                "errors": "Missing required fields in recipe"
            }), 400

        ingredient = Recipe(
            ingredient_name=recipe['name'],
            number_of_parts=recipe['parts'],
            color=recipe['color']
        )
        drink.recipes.append(ingredient)

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/drinks', methods=['GET'])
    def get_drinks():
        drinks = Drink.query.all()
        return jsonify({
            "success": True,
            "drinks": [drink.short() for drink in drinks]
        }), 200

    @app.route('/drinks-detail', methods=['GET'])
    @requires_auth('get:drinks-detail')
    def get_drinks_detail(payload):
        drinks = Drink.query.all()
        return jsonify({
            "success": True,
            "drinks": [drink.long() for drink in drinks]
        }), 200

    @app.route('/drinks', methods=['POST'])
    @requires_auth('post:drinks')
    def create_drink(payload):
        body = request.get_json()

        new_name = body.get('title', None)
        if new_name is None:
            return jsonify({
                "success": False,
                "errors": "Missing title in request body"
            }), 400

        drink = Drink(title=new_name)

        add_recipe(body, drink)

        drink.insert()

        return jsonify({
            "success": True,
            "drinks": drink.long()
        }), 201

    @app.route('/drinks/<int:id>', methods=['PATCH'])
    @requires_auth('patch:drinks')
    def update_drink(payload, id):
        body = request.get_json()
        drink = Drink.query.get(id)

        if drink is None:
            return jsonify({
                "success": False,
                "errors": "Drink not found"
            }), 404

        if 'title' in body:
            drink.title = body['title']

        drink.recipes.clear()
        add_recipe(body, drink)

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200

    @app.route('/drinks/<int:id>', methods=['DELETE'])
    @requires_auth('delete:drinks')
    def delete_drink(payload, id):
        drink = Drink.query.get(id)
        if drink is None:
            return jsonify({
                "success": False,
                "errors": "Drink not found"
            }), 404
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        }), 200

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "success": False,
            "errors": "Resource not found"
        }), 404

    return app
