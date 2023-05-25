from flask import Flask, send_file, render_template, request, jsonify
from flask_restx import Resource, Api, reqparse
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
import json
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from werkzeug.datastructures import FileStorage
from flask import send_file
from werkzeug.utils import secure_filename
import os
import cv2
import pytesseract
import pymysql
pymysql.install_as_MySQLdb()


app = Flask(__name__)
api = Api(app, title='Parking System MySQL', default='Input Data', default_label='Plat Nomor',
          description='Kelompok 5 : </br>'
                      'Buat Database : <a href="/create_db">Klik Buat</a></br>'
                      'History Database  : <a href="/all-data-parkir"><input type=submit value=Lihat></a>'
          )

# db.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:''@localhost/parkir1'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Parking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    no_plat = db.Column(db.String(50), unique=True)
    motor = db.Column(db.String(100), nullable=False)
    created_time = db.Column(db.TIMESTAMP, nullable=False)

@app.route("/create_db", methods=["GET"])
def create_db():
        with app.app_context():
            db.create_all()
            return "Database Telah dibuat" + ' <a href="/"> Kembali</a>'



class ParkingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Parking
        load_instance = True

@app.route("/all-data-parkir", methods=["GET"])
def getAllTilang():
    history = Parking.query.all()
    parking_schema = ParkingSchema(many=True)
    output = parking_schema.dump(history)
    return jsonify({'History Mysql': output})

app.config['UPLOAD_TILANG'] = 'folder_image'

parser4Param = reqparse.RequestParser()
parser4Param.add_argument('filename', type=str, help='Filename', location='args')

parser4Body = reqparse.RequestParser()
parser4Body.add_argument('file', location='files', type=FileStorage, required=True)

@api.route('/image/')
class ParkingAPI(Resource):
    @api.expect(parser4Body)
    def post(self):
            args = parser4Body.parse_args()
            file = args['file']
            motor = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_R'], motor))
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
            plate = cv2.imread("C:/Users/LENOVO/PycharmProjects/saya/assets/image/tilang" + file.filename)
            plate = cv2.cvtColor(plate, cv2.COLOR_BGR2RGB)

            no_plat = pytesseract.image_to_string(plate)

            parking = Parking(
                motor=motor,
                no_plat=no_plat,
            )
            db.session.add(parking)
            db.session.commit()
            return {
                'motor': motor,
                'no_plat':no_plat,
                'status': 200,
                'message': f"Data Motor dengan Nomor Plat {no_plat} telah ditambah"
            }

@api.route('/image/<string:no_plat>')
class ParkingAPI(Resource):
    def get(self, no_plat):
            parkings = db.session.execute(db.select(Parking).filter_by(no_plat=no_plat)).first()
            if (parkings is None):
                return f"Data Tilang Dengan Nomor Plat {no_plat} tidak ditemukan!"
            else:
                parking = parkings[0]
                return {
                    'METHOD': "GET",
                    'no_plat': parking.no_plat,
                    'motor': parking.motor,
                    'created_time': parking.created_time,
                    'status': 200,
                }

if __name__ == '__main__':
    # DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(debug=True)