from backend.model import db, app, api
from flask import Flask, send_file, request, jsonify, render_template, redirect, url_for, session, Response
from werkzeug.security import generate_password_hash
from datetime import datetime
from backend.model import LogUsers, LogParkir
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import pytesseract
import cv2
import os
import numpy as np
from keras.models import load_model
from assets.scan.live import cap
import mysql.connector
import time, datetime

from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app.secret_key = '$capsTone_pRoject_'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'big'

my = MySQL(app)

def frame_detect():
    cap = cv2.VideoCapture(0)

    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='big')
    cursor = cnx.cursor()

    classifier = cv2.CascadeClassifier("assets/scan/haarcascade_russian_plate_number.xml")
    minArea = 500

    i = 0

    while (cap.isOpened()):
        # Membaca frame dari kamera
        ret, frame = cap.read()

        if ret == True:
            # Mengubah frame ke grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect objek dari fra me grayscale
            plates = classifier.detectMultiScale(gray, 1.3, 5)

            # loop semua objek yang di deteksi
            for (x, y, w, h) in plates:
                area = w * h
                if area > minArea:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, "PlatNomor", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                    #memotong area objek yang di deteksi frame grayscale
                    roi_gray = gray[y:y + h, x:x + w]
                    cv2.imshow("IMG", roi_gray)
                    i = i + 1
                    filename = 'assets/image/Crop/Gambar Plat-' + str(i) + '.png'
                    cv2.imwrite(filename, roi_gray)
                    time.sleep(1)
                    if i < 4:
                        #Menggunakan pytesseract untuk mendeteksi plat motor dari gambar
                        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
                        text = pytesseract.image_to_string(filename)
                        capture_time = datetime.datetime.now()

                # Menyimpan data plat motor ke tabel MySQL
                        query = "INSERT INTO log_parkir (no_plat, tanggal) VALUES (%s, %s)"
                        cursor.execute(query, (text, capture_time))
                        cnx.commit()
                        # time.sleep(1)
                    else:
                        time.sleep(10)
                        i - 0
            frame = cv2.imencode('.jpg', frame)[1]
            encode = frame.tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + encode + b'\r\n')
            time.sleep(0.1)
        # else:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Register
@app.route("/register", methods=('GET', 'POST'))
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # tanggal = request.form['tanggal']
        cursor = my.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM log_users WHERE username = % s', (username,))
        log_users = cursor.fetchone()
        if log_users:
            msg = 'User already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO log_users VALUES (NULL, % s, % s, % s)', (username, email, password))
            my.connection.commit()
            msg = 'You have successfully registered !'
            return redirect(url_for('register'))
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template("tampilan/register/register.html")

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = my.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM log_users WHERE username = % s AND password = % s', (username, password, ))
        log_users = cursor.fetchone()
        if log_users:
            session['loggedin'] = True
            session['id'] = log_users['id']
            session['username'] = log_users['username']
            msg = 'logged in successfully !'
            return redirect(url_for('dasbor', msg = msg))
        else:
            msg = 'Username dan Password tidak cocok!'
    return render_template('tampilan/login/login.html', msg = msg)



# Dasbor
@app.route('/dasbor', methods=['GET', 'POST'])
def dasbor():
    return render_template("tampilan/dasbor/dashboard.html")

@app.route('/parkir', methods=['GET', 'POST'])
def parkir():
    if request.method == "GET":
        pr = LogParkir.query.all()
    return render_template("tampilan/parkir/data.html", parkir=pr)




@app.route('/landingg', methods=['GET', 'POST'])
def landingg():
    return render_template("tampilan/landingg/landing.html")

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    return render_template("tampilan/chat/chatbot2.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
     # Plat
        file = request.form['filename_plat']
        filename_plat = secure_filename(file.filename)
        file.save(os.path.join(app.config['FOLDER_PARKIR'], filename_plat))
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
        plate = cv2.imread(
            "C:/web_capstone/assets/image/parkir/" + file.filename)
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
    return render_template("tampilan/upload/upload.html")

@app.route('/scan')
def scan():
    return render_template("tampilan/scan/scan.html")

@app.route('/live')
def live():
    return Response(frame_detect(),mimetype='multipart/x-mixed-replace; boundary=frame')
