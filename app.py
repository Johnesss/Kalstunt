from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

cred = credentials.Certificate("smoke-f2db5-firebase-adminsdk-fbsvc-ee7a2eda68.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smoke-f2db5-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

def calculate_zscore(height, age_months, gender):
    if gender == 'L':
        average_height = [61, 71.7, 81.5, 89, 95.8, 102]
    else:
        average_height = [59, 69.8, 79.2, 87.8, 95, 101.1]

    age_index = min(age_months // 12, len(average_height) - 1)
    avg_height = average_height[age_index]

    z_score = (height - avg_height) / 2
    return z_score

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    status = None
    logs = []
    z_score = None

    if request.method == "POST":
        try:
            name = request.form["name"]
            age_months = int(request.form["age"])
            height = float(request.form["height"])
            gender = request.form["gender"]

            z_score = calculate_zscore(height, age_months, gender)

            if z_score < -2:
                status = f"{name} mengalami stunting!"
            else:
                status = f"{name} tidak mengalami stunting."

            ref_stunting = db.reference("/stunting_logs")
            ref_stunting.push({
                "name": name,
                "age_months": age_months,
                "height": height,
                "gender": gender,
                "z_score": z_score,
                "status": status
            })

            logs_ref = db.reference("/stunting_logs")
            logs = logs_ref.get()

        except Exception as e:
            result = f"Error: {e}"

    return render_template("index.html", result=result, status=status, logs=logs, z_score=z_score)

@app.route("/reset_history", methods=["POST"])
def reset_history():
    try:
        ref_stunting = db.reference("/stunting_logs")
        ref_stunting.delete()
        return redirect("/")
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
