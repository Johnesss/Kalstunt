from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, db

# Inisialisasi Flask
app = Flask(__name__)

# Firebase init
cred = credentials.Certificate("smoke-f2db5-firebase-adminsdk-fbsvc-ee7a2eda68.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smoke-f2db5-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Fungsi untuk menghitung Z-score
def calculate_zscore(height, age_months, gender):
    # Data WHO (misal dari CSV atau JSON yang berisi referensi tinggi badan)
    if gender == 'L':
        # Data tinggi badan laki-laki untuk usia 0-5 tahun (contoh data, harusnya dari WHO)
        average_height = [50, 55, 60, 65, 70, 75]
    else:
        # Data tinggi badan perempuan untuk usia 0-5 tahun (contoh data, harusnya dari WHO)
        average_height = [50, 54, 59, 64, 69, 74]

    # Menentukan usia berdasarkan bulan dan mengambil referensi tinggi badan
    age_index = min(age_months - 1, len(average_height) - 1)
    avg_height = average_height[age_index]

    # Hitung Z-score
    z_score = (height - avg_height) / 2  # Asumsi deviasi standar 2 cm untuk contoh ini
    return z_score

# Route utama
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    status = None
    logs = []

    if request.method == "POST":
        try:
            # Ambil input dari form
            name = request.form["name"]
            age_months = int(request.form["age"])
            height = float(request.form["height"])
            weight = float(request.form["weight"])
            gender = request.form["gender"]

            # Hitung Z-score
            z_score = calculate_zscore(height, age_months, gender)

            # Tentukan status stunting
            if z_score < -2:
                status = f"{name} mengalami stunting!"
            else:
                status = f"{name} tidak mengalami stunting."

            # Simpan data ke Firebase
            ref_stunting = db.reference("/stunting_logs")
            ref_stunting.push({
                "name": name,
                "age_months": age_months,
                "height": height,
                "weight": weight,
                "gender": gender,
                "z_score": z_score,
                "status": status
            })

            # Ambil history dari Firebase
            logs_ref = db.reference("/stunting_logs")
            logs = logs_ref.get()

        except Exception as e:
            result = f"Error: {e}"

    return render_template("index.html", result=result, status=status, logs=logs)

# Route untuk mereset history
@app.route("/reset_history", methods=["POST"])
def reset_history():
    try:
        # Menghapus data stunting logs di Firebase
        ref_stunting = db.reference("/stunting_logs")
        ref_stunting.delete()  # Menghapus semua data
        return redirect("/")  # Mengarahkan kembali ke halaman utama setelah reset
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

