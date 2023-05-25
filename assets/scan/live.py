from flask import Flask, render_template, request
import cv2
import pytesseract
import mysql.connector
import datetime
import time

app = Flask(__name__)

# Membuat koneksi ke database MySQL
cnx = mysql.connector.connect(user='root', password='', host='localhost', database='coba')
cursor = cnx.cursor()

# Load classifier for HAAR Cascade
classifier = cv2.CascadeClassifier("haarcascade_russian_plate_number.xml")
minArea = 500

# Membuka kamera
cap = cv2.VideoCapture(0)

@app.route('/scan')
def index():
    return render_template('live.html')

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

if __name__ == '__main__':
    app.run(debug=True)

# Menutup koneksi ke kamera dan database MySQL
cap.release()
cursor.close()
cnx.close()
cv2.destroyAllWindows()
