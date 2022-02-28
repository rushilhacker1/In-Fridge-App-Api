#Imports
from ast import arg
from enum import unique
from flask import jsonify,Flask
from flask_restful import Resource,abort,Api,reqparse,fields,marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

#Inits
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['DEBUG'] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)

#variables
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'Email': fields.String
}
resource_fields_dish = {
    'id': fields.Integer,
    'dishname': fields.String,
    'ingridents': fields.String,
    "link": fields.String
}
#DataBase Tables
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    Email = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"User(name = {self.name}, Email = {self.Email})"

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dishname = db.Column(db.String(100), nullable=False)
    ingridents = db.Column(db.String, nullable=False)
    link = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"Dish(dishname = {self.dishname}, ingridents = {self.ingridents}, link = {self.ingridents})"

#Args
user_put_args = reqparse.RequestParser()
user_put_args.add_argument("name", type=str, help="Name of the user is required", required=True)
user_put_args.add_argument("Email", type=str, help="Views of the user", required=True)

dish_put_args = reqparse.RequestParser()
dish_put_args.add_argument("dishname", type=str, help="Name of the user is required", required=True)
dish_put_args.add_argument("ingridents", type=str, help="Name of the user is required", required=True)
dish_put_args.add_argument("link", type=str, help="Name of the user is required", required=True)


user_patch_args = reqparse.RequestParser()
user_patch_args.add_argument("name", type=str, help="Name of the user is required", )
user_patch_args.add_argument("Email", type=str, help="Views of the user")

dish_patch_args = reqparse.RequestParser()
dish_patch_args.add_argument("dishname", type=str, help="Name of the user is required")
dish_patch_args.add_argument("ingridents", type=str, help="Name of the user is required")
dish_patch_args.add_argument("link", type=str, help="Name of the user is required")
#Marshmallow Schemas
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

    id = ma.auto_field()
    name = ma.auto_field()
    Email = ma.auto_field()

class DishSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Dish

    id = ma.auto_field()
    dishname = ma.auto_field()

#Creates db
db.create_all()

#Resource Classes
class Users(Resource):
    def get(self, user_id):
        dishschema = UserSchema()
        model = User.query.filter_by(id=user_id).first()
        data = dishschema.dump(model)
        print(model)
        print(data)
        if not model:
            abort(404,message="user not found")
        return jsonify(data)


    def put(self,user_id):
        userschema = UserSchema()
        args = user_put_args.parse_args()
        data = User(name = args['name'], Email = args['Email'])
        db.session.add(data)
        db.session.commit()
        return jsonify(userschema.dump(data))

    @marshal_with(resource_fields)
    def patch(self, user_id):
        args = user_patch_args.parse_args()
        result = User.query.filter_by(id=user_id).first()
        if not result:
            abort(404, message="User doesn't exist, cannot update")

        if args['name']:
            result.name = args['name']
        if args['Email']:
            result.Email = args['Email']

        db.session.commit()

        return result

    def delete(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found")
        User.query.filter_by(id=user_id).delete()
        db.session.commit()
        return '', 204

class AllUsers(Resource):
    @marshal_with(resource_fields)
    def get(self):
        model = User.query.all()
        print(model)
        return model

class Dishes(Resource):
    def get(self, dish_id):
        dishschema = DishSchema()
        model = Dish.query.filter_by(id=dish_id).first()
        data = dishschema.dump(model)
        data['ingridents'] = model.ingridents.split()

        if not model:
            abort(404,message="user not found")
        return jsonify(data)

    def put(self,dish_id):
        dishschema = DishSchema()
        args = dish_put_args.parse_args()
        args['ingridents']
        data = Dish(dishname = args['dishname'], ingridents = args['ingridents'], link = args['link'])
        db.session.add(data)
        db.session.commit()
        return jsonify(dishschema.dump(data))

    @marshal_with(resource_fields_dish)
    def patch(self, dish_id):
        args = dish_patch_args.parse_args()
        result = Dish.query.filter_by(id=dish_id).first()
        if not result:
            abort(404, message="User doesn't exist, cannot update")

        if args['dishname']:
            result.dishname = args['dishname']

        if args['ingridents']:
            result.ingridents = args['ingridents']

        if args['link']:
            result.link = args['link']

        print(result)

        db.session.commit()

        return result
class AllDishes(Resource):
    @marshal_with(resource_fields_dish)
    def get(self):
        model = Dish.query.all()
        print()
        print(model)
        return model


api.add_resource(Users, "/user/<int:user_id>")
api.add_resource(AllUsers, "/user/")
api.add_resource(Dishes, "/dishes/<int:dish_id>")
api.add_resource(AllDishes, "/dishes/")

if __name__ == '__main__': 
    app.run()
