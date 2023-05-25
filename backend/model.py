from flask import Flask, send_file, request, jsonify, render_template, redirect, url_for, session
from flask_restx import Resource, Api, reqparse

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
api = Api(app, title='PARKIR SISTEM', default='API', default_label='PARKIR SISTEM', )

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:''@localhost/big'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['FOLDER_PARKIR'] = 'assets/image/parkir'

db = SQLAlchemy(app)
ma = Marshmallow(app)

##################################### Database Parkir ###########################################
class LogParkir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    no_plat = db.Column(db.String(50), nullable=False)
    filename_plat = db.Column(db.String(200), nullable=False)
    tanggal = db.Column(db.DATETIME, nullable=False)

    def __init__(self, no_plat, filename_plat, tanggal):
        self.no_plat = no_plat
        self.filename_plat = filename_plat
        self.tanggal = tanggal

class ParkirSchema(ma.SQLAlchemyAutoSchema):
     class Meta:
        model = LogParkir
        load_instance = True

parser4Param = reqparse.RequestParser()
parser4Param.add_argument('file', location='files', help='Filename Plat', type=FileStorage, required=True)

parser4Body = reqparse.RequestParser()
parser4Body.add_argument('file', location='files', help='Filename Plat', type=FileStorage, required=True)


################################# Database User ###########################################
class LogUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class SchemaUsers(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LogUsers
        load_instance = True


parserParamUsers = reqparse.RequestParser()
parserParamUsers.add_argument('username', type=str, help='Masukan Username', location='args')
parserParamUsers.add_argument('email', type=str, help='Masukan Email', location='args')
parserParamUsers.add_argument('password', type=str, help='Masukan Password', location='args')

parserBodyUsers = reqparse.RequestParser()
parserBodyUsers.add_argument('username', type=str, help='Masukan Username', location='args')
parserBodyUsers.add_argument('email', type=str, help='Masukan Email', location='args')
parserBodyUsers.add_argument('password', type=str, help='Masukan Password', location='args')