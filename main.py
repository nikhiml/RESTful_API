from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#Cafe TABLE Configuration
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
        result = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return result


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def get():
    all_cafe = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafe)
    return jsonify(random_cafe.to_dict())

    # return jsonify(cafe={"id": random_cafe.id, "name": random_cafe.name, "map_url": random_cafe.map_url,
    #                      "img_url": random_cafe.img_url, "location": random_cafe.location, "seats": random_cafe.seats,
    #                      "amenities": {"has_toilet": random_cafe.has_toilet, "has_wifi": random_cafe.has_wifi,
    #                      "has_sockets": random_cafe.has_sockets, "can_take_calls": random_cafe.can_take_calls},
    #                      "coffee_price": random_cafe.coffee_price})


@app.route('/all')
def all_cafes():

    all_cafe = db.session.query(Cafe).all()

    # Option 1: Using dictionary comprehension code:
    return jsonify(cafe=[cafe.to_dict() for cafe in all_cafe])

    # Option 2: Using extended code:
    # all_cafes_dict = {"cafes": []}
    # for cafe in all_cafe:
    #     cafe_dict = cafe.to_dict()
    #     all_cafes_dict['cafes'].append(cafe_dict)
    # return jsonify(all_cafes_dict)


@app.route('/search')
def search_by_location():
    location = request.args.get("loc")
    cafe_in_location = Cafe.query.filter_by(location=location).all()
    if cafe_in_location:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafe_in_location])
    else:
        return "No cafe in the specified location"

@app.route('/add', methods=['GET', 'POST'])
def add_cafe():

    # Option 1: Using request.form['field name'] method
    new_cafe = Cafe(name=request.form['name'], map_url=request.form['map_url'], img_url=request.form['img_url'],
                    location=request.form['location'], seats=request.form['seats'], has_toilet=bool(request.form['has_toilet']),
                    has_wifi=bool(request.form['has_wifi']), has_sockets=bool(request.form['has_sockets']),
                    can_take_calls=bool(request.form['can_take_calls']), coffee_price='NA')

    # Option 2: Using request.form.get('') method
    # new_cafe = Cafe(name=request.form.get('name'), map_url=request.form.get('map_url'), img_url=request.form.get('img_url'),
    #                 location=request.form.get('location'), seats=request.form.get('seats'), has_toilet=bool(request.form.get('has_toilet')),
    #                 has_wifi=bool(request.form.get('has_wifi')), has_sockets=bool(request.form.get('has_sockets')),
    #                 can_take_calls=bool(request.form.get('can_take_calls')), coffee_price=request.form.get('coffee_price'))


    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={'success': 'Added New Cafe'})


@app.route('/update_price/<cafe_id>')
def update_price(cafe_id):
    new_price = request.args.get('price')
    cafe_to_update = Cafe.query.filter_by(id=cafe_id).first()
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={'success': 'Price Updated'}), 200
    else:
        return jsonify(error={'Failure': 'Cafe Not Found'}), 404


@app.route('/delete-cafe/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    user_api_key = request.args.get('api_key')
    if user_api_key == 'TopSecretKey':
        print('inside first if')
        cafe_to_delete = Cafe.query.filter_by(id=cafe_id).first()
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(result={'Success': 'Cafe Successfully Deleted'}), 200
        else:
            return jsonify(error={'Not Found': 'Sorry cannot find the cafe'}), 404
    else:
        return jsonify(error={'Not Allowed': 'No Permission'}), 403


if __name__ == '__main__':
    app.run(debug=True)
