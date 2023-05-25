import cv2
import pytesseract
import mysql.connector
import datetime
import time

from backend.live import scan
from backend.model import app
from flask import Flask, render_template, request
from backend.API import parkir, users

import nltk
nltk.download('popular')
import nltk
nltk.download('popular')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model = load_model('assets/model_chatbot/chatbot_model.h5')
import json
import random

from backend import chatbot
from backend.chatbot import model, load_model,chatbot_response,getResponse,get_bot_response,clean_up_sentence,predict_class,lemmatizer
from backend.chatbot import intents, words, classes

from backend import backend
from backend.backend import dasbor, parkir, landingg, upload, scan, live, login, register
from backend.API.parkir import getAllParkir, ParkirAPI
from backend.API.users import getAllUsers, UserAPI, flutter_register


# Route API
@app.route("/api/parkir")
# @app.route("/users")
# @app.route("/parkir")
# @app.route("/login")
# @app.route("/register")
# @app.route("/dasbor")

# Route Chatbot
@app.route("/landing/chatbot")
def home():
    return render_template("tampilan/chat/chatbot2.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)

# live
# Membuat koneksi ke database MySQL
cnx = mysql.connector.connect(user='root', password='', host='localhost', database='coba')
cursor = cnx.cursor()

# Load classifier for HAAR Cascade
classifier = cv2.CascadeClassifier("assets/scan/haarcascade_russian_plate_number.xml")
minArea = 500

# Membuka kamera
cap = cv2.VideoCapture(0)


@app.route('/detect', methods=['POST'])
def detect():
    # Membaca frame dari kamera
    ret, frame = cap.read()
    # Mengubah frame ke grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect plate number using HAAR Cascade
    plates = classifier.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in plates:
        area = w*h
        if area > minArea:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,0,255), 2)
            cv2.putText(frame,"PlatNomor",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
            roi_gray = gray[y:y+h, x:x+w]
            cv2.imshow("IMG",roi_gray)

        # Menggunakan pytesseract untuk mendeteksi plat motor dari gambar
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
        text = pytesseract.image_to_string(roi_gray)
        capture_time = datetime.datetime.now()

        # Menyimpan data plat motor ke tabel MySQL
        query = "INSERT INTO log_parkir (no_plat, tanggal) VALUES (%s, %s)"
        cursor.execute(query, (text, capture_time))
        cnx.commit()
        time.sleep(1)

    # Tampilkan frame yang diambil dari kamera
    cv2.imshow("Frame", frame)
    return "Plate Number: {} captured at {}".format(text, capture_time)

# Menutup koneksi ke kamera dan database MySQL
cap.release()
cursor.close()
cnx.close()
cv2.destroyAllWindows()

if __name__ == '__main__':
    app.run(debug=True)