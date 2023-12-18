from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    jsonify,
    make_response,
    current_app,
    flash,
)
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import requests, os
import hashlib
from datetime import datetime, timedelta
from bson import ObjectId
import jwt
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from os.path import join, dirname
from dotenv import load_dotenv
from babel.numbers import format_currency
from functools import wraps


app = Flask(__name__)
# Atur folder untuk menyimpan file di direktori 'static'
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config['SECRET_KEY'] = 'SPARTA'

MONGODB_CONNECTION_STRING = (
    "mongodb+srv://ilham123:ilham123@cluster0.z5oy8if.mongodb.net/?retryWrites=true&w=majority"
)
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.FINAL_PROJECT

SECRET_KEY = "SPARTA"
# # Memberikan SECRET_KEY
# app.config['SECRET_KEY'] = 'SPARTA'




# HOME
@app.route("/")
def index_page():
    return render_template("index_page.html")


# PENDAFTAR
# Login Pendaftar
@app.route("/login/user", methods=["GET", "POST"])
def login_user():
    # Jika methods POST
    if request.method == "POST":
        username_receive = request.form.get("username_give")
        password_receive = request.form.get("password_give")

        password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

        result = db.user.find_one(
            {
                "username": username_receive,
                "password": password_hash,
            }
        )

        if result is not None:
            payload = {
                "username": username_receive,
                "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return jsonify({"result": "success", "token": token})
        else:
            return jsonify(
                {
                    "result": "fail",
                    "msg": "Terdapat kesalahan pada username atau Password anda!",
                }
            )

    # GET
    msg = request.args.get("msg")
    return render_template("login_pendaftar.html", msg=msg)


    # # Jika methods GET
    # token_receive = request.cookies.get(SECRET_KEY)
    # if token_receive:
    #     try:
    #         payload = jwt.decode(
    #             token_receive,
    #             SECRET_KEY,
    #             algorithms=['HS256']
    #         )
    #         # Jika pengguna sudah login, arahkan ke halaman dashboard
    #         return redirect(url_for('dashboard'))

    #     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
    #         # Token tidak valid, lanjutkan ke halaman login
    #         pass

    # # GET
    # msg = request.args.get("msg")
    # return render_template("login_pendaftar.html", msg=msg)


@app.route("/artikel")
def artikel():
    return render_template("artikel.html")


@app.route("/dashboard")
def dashboard():
    token_receive = request.cookies.get(SECRET_KEY)

    if token_receive:
        try:
            payload = jwt.decode(
                token_receive,
                SECRET_KEY,
                algorithms=['HS256']
            )
            user_info = db.user.find_one({'username': payload.get('id')})
            return render_template('dashboard.html', user_info=user_info)

        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            msg = 'You are not logged in!'
        return redirect(url_for('login_user'))

# Jika tidak ada token atau token tidak valid, arahkan ke dashboard
    return render_template('dashboard.html')


@app.route("/pendaftaran")
def halamanan_pendaftaran():
    return render_template("pendaftaran.html")


@app.route("/pendaftaran", methods=["POST"])

def pendaftaran():
    nama = request.form["nama"]
    jenisKelamin = request.form["jenisKelamin"]
    alamat = request.form["alamat"]
    no = request.form["no"]
    asal = request.form["asal"]
    ijazah = request.files["ijazah"]
    kk = request.files["kk"]

    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")

    ijazah_save = f'static/file/ijazah-{mytime}.{ijazah.filename.split(".")[-1]}'
    kk_save = f'static/file/kk-{mytime}.{kk.filename.split(".")[-1]}'

    ijazah.save(ijazah_save)
    kk.save(kk_save)

    time = today.strftime("%Y-%m-%d")

    doc = {
        "nama": nama,
        "jenisKelamin": jenisKelamin,
        "alamat": alamat,
        "no": no,
        "asal": asal,
        "ijazah": ijazah_save,
        "kk": kk_save,
        "time": time,
    }
    db.pendaftaran.insert_one(doc)
    return render_template("pendaftaran.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/status_pendaftaran")
def status_pendaftaran():
    return render_template("status_pendaftaran.html")


@app.route("/kontak")
def kontak_kami():
    return render_template("kontak_kami.html")


@app.route("/register/user", methods=["GET", "POST"])
def register_user():
    # Jika methods POST
    if request.method == "POST":
        username_receive = request.form.get("username_give")
        email_receive = request.form.get("email_give")
        password_receive = request.form.get("password_give")

        # Hashing password
        password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

        # Data yang akan disimpan
        doc = {
            "username": username_receive,
            "email": email_receive,
            "password": password_hash,
            "nama": username_receive,
        }

        # Masukkan data ke database
        db.user.insert_one(doc)

        return jsonify({"result": "success"})

    # Jika methods GET
    msg = request.args.get("msg")
    return render_template("registrasi.html", msg=msg)


# ADMIN


# Login Admin
@app.route("/login/admin", methods=["GET", "POST"])
def login_admin():
    # Jika methods POST
    if request.method == "POST":
        id_receive = request.form.get("id_give")
        password_receive = request.form.get("password_give")

        password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

        result = db.admin.find_one(
            {
                "id": id_receive,
                "password": password_hash,
            }
        )

        if result is not None:
            payload = {
                "id": id_receive,
                "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return jsonify({"result": "success", "token": token})
        else:
            return jsonify(
                {
                    "result": "fail",
                    "msg": "Terdapat kesalahan pada ID atau Password anda!",
                }
            )

    # Jika methods GET
    msg = request.args.get("msg")
    return render_template("login_admin.html", msg=msg)


@app.route("/admin")
def admin():
    data = db.pendaftaran.find()
    return render_template("dashboard_admin.html", data=data)


@app.route("/update/<id>", methods=["GET", "POST"])
def update(id):
    data = db.pendaftaran.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        updated_data = {
            "nama": request.form["nama"],
            "asal": request.form["asal"],
            "status": request.form["status"],
            # ... (tambahkan bidang lainnya sesuai kebutuhan)
        }

        db.pendaftaran.update_one({"_id": ObjectId(id)}, {"$set": updated_data})

        return redirect(url_for("admin"))

    return render_template("update.html", data=data)


@app.route("/hapus/<id>")
def hapus(id):
    # Mendapatkan data pendaftaran yang akan dihapus
    data = db.pendaftaran.find_one({"_id": ObjectId(id)})

    # Menghapus file Ijazah dan Kartu Keluarga dari direktori
    if data:
        os.remove(data["ijazah"])
        os.remove(data["kk"])

    # Menghapus data dari database
    db.pendaftaran.delete_one({"_id": ObjectId(id)})

    return redirect(url_for("admin"))


@app.route("/va")
def va():
    return render_template("verif_admin.html")


@app.route("/profile_admin")
def profile_admin():
    return render_template("profile_admin.html")


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
