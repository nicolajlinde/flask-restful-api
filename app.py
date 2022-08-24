from flask import Flask, jsonify, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from random import choice
from flask import jsonify
from pprint import pprint
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/random')
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def get_all_cafes():
    cafes = Cafe.query.all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route('/search')
def search_cafes_in_location():
    query_location = request.args.get("loc")
    search = Cafe.query.filter_by(location=query_location).all()
    if search:
        return jsonify(cafe=[cafe.to_dict() for cafe in search])
    else:
        return jsonify({
            "error": {
                "Not Found": "Sorry, we don't have a cafe at that location."
            }
        })


# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_cafe():
    if request.method == 'POST':
        new_cafe = Cafe(
            name=request.form.get('name'),
            map_url=request.form.get('map_url'),
            img_url=request.form.get('img_url'),
            location=request.form.get('location'),
            has_sockets=bool(request.form.get('has_sockets')),
            has_toilet=bool(request.form.get('has_toilet')),
            has_wifi=bool(request.form.get('has_wifi')),
            can_take_calls=bool(request.form.get('can_take_calls')),
            seats=request.form.get('seats'),
            coffee_price=request.form.get('coffee_price'),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:id>', methods=['PATCH'])
def update_cafe_price(id):
    new_price = request.args.get("new_price")
    if id and new_price:
        cafe = Cafe.query.filter_by(id=id).first()
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated price on cafe."})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


# HTTP DELETE - Delete Record
@app.route('/delete/cafe/<int:id>', methods=['DELETE'])
def delete_cafe(id):
    api_key = request.args.get("api_key")
    if id and api_key == API_KEY:
        cafe = Cafe.query.filter_by(id=id).first()
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted a cafe."})
        else:
            return jsonify(error={
                "Not Found": "Sorry, a cafe with that id was not found in the database"})
    else:
        return jsonify({"error": "Sorry, that's not allowed. Make sure you have the correct api_key"})


if __name__ == '__main__':
    app.run()
