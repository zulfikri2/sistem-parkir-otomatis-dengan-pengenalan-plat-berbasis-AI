from backend.model import db, app, api, LogParkir, ParkirSchema, parser4Param, parser4Body
from flask import Flask, send_file, request, jsonify, render_template, redirect, url_for, session
from flask_restx import Resource, Api, reqparse
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import datetime
import pytesseract
import cv2
from PIL import Image
import os
import numpy as np
from keras.models import load_model
from keras.models import Sequential

# create db parkir
@app.route("/api/create_image", methods=["GET"])
def create_db():
    with app.app_context():
        db.create_all()
        return "Database Telah dibuat" + ' <a href="/"> Kembali</a>'


@app.route("/api/parkir", methods=["GET"])
def getAllParkir():
    history = LogParkir.query.all()
    parkir_schema = ParkirSchema(many=True)
    output = parkir_schema.dump(history)
    return jsonify(output)
#swager
@api.route('/api/parkir')
class ParkirAPI(Resource):
    def get(self):
        log_data = db.session.execute(
            db.select(LogParkir.id, LogParkir.no_plat, LogParkir.filename_plat)).all()
        if (log_data is None):
            return f"Tidak Ada Data Parkir!"
        else:
            data = []
            for history in log_data:
                data.append({
                    'id': history.id,
                    'no_plat': history.no_plat,
                    'filename_plat': history.filename_plat,

                })
            return data

    @api.expect(parser4Body)
    def post(self):
        args = parser4Body.parse_args()

        # Plat
        file = args['file']
        filename_plat = secure_filename(file.filename)
        file.save(os.path.join(app.config['FOLDER_PARKIR'], filename_plat))
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
        plate = cv2.imread(
            "C:/Users/LENOVO/PycharmProjects/saya/assets/image/parkir/" + file.filename)
        plate = cv2.cvtColor(plate, cv2.COLOR_BGR2RGB)
        no_plat = pytesseract.image_to_string(plate)


# ---------------------------------------------------------------
        tanggal = datetime.now()
        tanggal_baru = tanggal.strftime('%Y-%m-%d %H:%M:%S')

        parkir = LogParkir(
            no_plat=no_plat,
            filename_plat=filename_plat,
            tanggal=tanggal_baru,
        )
        db.session.add(parkir)
        db.session.commit()
        return {
            'no_plat': no_plat,
            'filename_plat': filename_plat,
            'tanggal': tanggal_baru,
            'status': 200,
            'message': f"Data  dengan Nomor Plat {no_plat} telah ditambah"
        }

# Delete
@api.route('/api/<string:no_plat>')
class ParkirAPI(Resource):
    def delete(self, no_plat):
        parkings = db.session.execute(db.select(LogParkir).filter_by(no_plat=no_plat)).first()
        if (parkings is None):
            return f"Data Parkir dengan Nomor Plat {no_plat} tidak ditemukan!"
        else:
            parkir = parkings[0]
            db.session.delete(parkir)
            db.session.commit()
            return f"Data Parkir dengan Nomor Plat {no_plat} berhasil dihapus!"

