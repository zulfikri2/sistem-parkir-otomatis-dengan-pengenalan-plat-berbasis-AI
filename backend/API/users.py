from backend.model import db, app, api, LogUsers, parserParamUsers, parserBodyUsers, SchemaUsers
from flask import Flask, send_file, request, jsonify, render_template, redirect, url_for, session
from flask_restx import Resource, Api, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash
from datetime import datetime


@app.route("/api/create_user", methods=["GET"])
def users_db():
    with app.app_context():
        db.create_all()
        return "Database User Telah dibuat" + ' <a href="/"> Kembali</a>'


@app.route("/api/user", methods=["GET"])
def getAllUsers():
    history = LogUsers.query.all()
    users_schema = SchemaUsers(many=True)
    output = users_schema.dump(history)
    return jsonify(output)


@api.route('/api/user', methods=["GET", "POST"])
class UserAPI(Resource):
    def get(self):
        log_data = db.session.execute(
            db.select(LogUsers.id, LogUsers.username, LogUsers.email, LogUsers.password)).all()
        if (log_data is None):
            return f"Tidak Ada Data User!"
        else:
            data = []
            for user in log_data:
                data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'password': user.password
                })
            return data

    @api.expect(parserBodyUsers)
    def post(self):
        d = {}
        if request.method == "POST":
            args = parserBodyUsers.parse_args()
            username = args["username"]
            mail = args["email"]
            password = args["password"]

            email = LogUsers.query.filter_by(email=mail).first()

            if email is None:
                register = LogUsers(username=username, email=mail, password=password)

                db.session.add(register)
                db.session.commit()

                return jsonify(["Register success"])
            else:
                return jsonify(["Data Sudah Terdaftar"])


# Delete Image
@api.route('/user/<string:email>')
class UserAPI(Resource):
    def delete(self, email):
        users = db.session.execute(db.select(LogUsers).filter_by(email=email)).first()
        if (users is None):
            return f"Data User dengan Email {email} tidak ditemukan!"
        else:
            parkir= users[0]
            db.session.delete(parkir)
            db.session.commit()
            return f"Data User dengan Email {email} berhasil dihapus!"


@app.route('/api/register', methods=["GET", "POST"])
def flutter_register():
    d = {}
    if request.method == "POST":
        username = request.form["username"]
        mail = request.form["email"]
        password = request.form["password"]

        email = LogUsers.query.filter_by(username=username, email=mail, password=password).first()

        if email is None:
            register = LogUsers(username=username, email=mail, password=password)

            db.session.add(register)
            db.session.commit()

            return jsonify(["Register success, Silahkan Login!"])
        else:
            # already exist

            return jsonify(["Username Sudah Ada, Cek Ulang!"])


@app.route('/api/login', methods=["GET", "POST"])
def flutter_login():
    d = {}
    if request.method == "POST":
        mail = request.form["email"]
        password = request.form["password"]

        email = LogUsers.query.filter_by(email=mail, password=password).first()

        if email is None:
            # acount not found
            return jsonify(["Login Gagal, Cek Kembali!"])
        else:
            # acount found
            return jsonify(["Login Success, Selamat Datang!"])