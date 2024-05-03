"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Users, People, Planets, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_hello():
    users = Users.query.all()
    serialize_user = list(map(lambda x: x.serialize(), users))
    return serialize_user, 200
    
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.json.get('user_id')
    print(user_id)
    user = Users.query.get(user_id)
    if user is None:
        return jsonify({"msg": "User not found"}), 404
    favorites = user.favorites
    favorites_list = [fav.serialize() for fav in favorites]
    return jsonify(favorites_list), 200

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    serialize_people = list(map(lambda x: x.serialize(), people))
    return serialize_people, 200
    
@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    single_people = People.query.get(people_id)
    if single_people is None:
        return jsonify({"msg":"People not found"}), 404
    serialize_one_people = single_people.serialize()
    return serialize_one_people, 200
    
@app.route('/planets', methods=['GET'])
def get_planets():
    planet = Planets.query.all()
    serialize_planet = list(map(lambda x: x.serialize(), planet))
    return serialize_planet, 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planets_by_id(planet_id):
    single_planet = Planets.query.get(planet_id)
    if single_planet is None:
        return jsonify({"msg":"Planet not found"}), 404
    serialize_one_planet = single_planet.serialize()
    return serialize_one_planet, 200

@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['POST'])
def add_planet_favorite(planet_id, user_id):
    new_favorite = Favorites(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"message": "Planet added to favorites successfully"}), 200

@app.route('/favorite/people/<int:people_id>/<int:user_id>', methods=['POST'])
def add_people_favorite(people_id, user_id):
    new_favorite = Favorites(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"message": "People added to favorites successfully"}), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):
    user_id = request.json.get('user_id')
    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Planet favorite deleted successfully"}), 200
    else:
        return jsonify({"message": "Planet favorite not found"}), 404

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_favorite(people_id):
    user_id = request.json.get('user_id')
    favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "People favorite deleted successfully"}), 200
    else:
        return jsonify({"message": "People favorite not found"}), 404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
