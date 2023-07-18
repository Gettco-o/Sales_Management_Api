from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, db_drop_and_create_all
from auth import AuthError
import os
from dotenv import load_dotenv

load_dotenv()

app =Flask(__name__)
app.config['SECRET_KEY']=os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

db.init_app(app)

migrate = Migrate(app, db)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))

#with app.app_context():
#    db_drop_and_create_all()

from main import main as main_blueprint
app.register_blueprint(main_blueprint)


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify(
        {
            'success': False,
            'error': 404,
            'message': 'resource_not_found'
        }
    ), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify(
        {
            'success': False,
            'error': 400,
            'message': 'bad request'
        }
    ), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify(
        {
            'success': False,
            'error': 401,
            'message': 'unauthorized'
        }
    )

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(
        {
            'success': False,
            'error': 405,
            'message': 'method_not_allowed'
        }
    ), 405


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify(
        {
            'success': False,
            'error': error.status_code,
            'message': error.error
        }
    ), error.status_code
