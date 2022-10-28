from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

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

    def cafe_dictionary(self):
        cafe = {
            "id": self.id,
            "name": self.name,
            "map_url": self.map_url,
            "img_url": self.img_url,
            "location": self.location,
            "seats": self.seats,
            "has_toilet": self.has_toilet,
            "has_wifi": self.has_wifi,
            "has_sockets": self.has_sockets,
            "can_take_calls": self.can_take_calls,
            "coffee_price": self.coffee_price
        }
        return cafe


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random():
    rand_cafe = random.choice(db.session.query(Cafe).all())
    return jsonify({"cafe": rand_cafe.cafe_dictionary()})


@app.route("/all")
def get_all():
    all_cafes = {"cafes": [cafe.cafe_dictionary() for cafe in db.session.query(Cafe).all()]}
    return jsonify(all_cafes)


@app.route("/search")
def search():
    loc = request.args.get("loc")
    all_cafes = [{"cafe": cafe.cafe_dictionary()} for cafe in db.session.query(Cafe).all() if cafe.location == loc]
    err = {"error": {"Not found": "Sorry, we don't have a cafe in that location."}}
    return jsonify(all_cafes) if all_cafes != [] else jsonify(err), 404


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add():
    err = {"response": {"error": "Sorry, we weren't able to add the cafe."}}
    success = {"response": {"success": "Successfully added the new cafe."}}
    try:
        cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("has_sockets")),
            has_toilet=bool(request.form.get("has_toilet")),
            has_wifi=bool(request.form.get("has_wifi")),
            can_take_calls=bool(request.form.get("can_take_calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),)
        db.session.add(cafe)
        db.session.commit()
    except Exception:
        return jsonify(err), 400
    else:
        return jsonify(success)


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    err = {"error": {"Not found": "Sorry, we don't have a cafe with that id."}}
    success = {"response": {"success": "Successfully updated the price."}}
    try:
        coffee_price = request.form.get("coffee_price")
        cafe = Cafe.query.get(cafe_id)
        cafe.coffee_price = coffee_price
        db.session.commit()
    except Exception:
        return jsonify(err), 404
    else:
        return jsonify(success)


# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    err = {"error": {"Not found": "Sorry, we don't have a cafe with that id."}}
    no_auth = {"error": {"Authorization Denied": "Sorry, you are not allowed to delete cafes."}}
    success = {"response": {"success": "Successfully deleted the cafe."}}

    if request.args.get("api-key") != "TopSecretApiKey":
        return jsonify(no_auth), 403
    try:
        cafe = Cafe.query.get(cafe_id)
        db.session.delete(cafe)
        db.session.commit()
    except Exception:
        return jsonify(err), 404
    else:
        return jsonify(success)


if __name__ == '__main__':
    app.run(debug=True)
