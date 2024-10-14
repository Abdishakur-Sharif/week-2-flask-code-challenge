#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
import os

# Initialize the Flask application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = []
    for restaurant in Restaurant.query.all():
        restaurant_dict = restaurant.to_dict()
        restaurants.append(restaurant_dict)

    return make_response(restaurants, 200, {"Content-Type": "application/json"})

@app.route('/restaurants/<int:id>')
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if restaurant:
        restaurant_dict = restaurant.to_dict()
        return make_response(restaurant_dict, 200)
    else:
        return make_response({"error": "Restaurant not found"}, 404)


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant:
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return make_response({"error": "Restaurant not found"}, 404)


@app.route('/pizzas')
def get_pizzas():
        pizzas = []
        for pizza in Pizza.query.all():
            pizza_dict = pizza.to_dict()
            pizzas.append(pizza_dict)

        return make_response(pizzas, 200, {"Content-Type": "application/json"})
   

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if price is None or not (1 <= price <= 30):
        return make_response({"errors": ["validation errors"]}, 400)

    pizza = Pizza.query.filter(Pizza.id == pizza_id).first()
    restaurant = Restaurant.query.filter(Restaurant.id == restaurant_id).first()

    if not pizza or not restaurant:
        return make_response({"errors": ["Pizza or Restaurant not found"]}, 404)

    restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    db.session.add(restaurant_pizza)
    db.session.commit()

    return make_response({
        "id": restaurant_pizza.id,
        "pizza_id": pizza.id,
        "price": restaurant_pizza.price,
        "restaurant_id": restaurant.id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients  
        },
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address 
        }
    }, 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
