from flask import Flask, render_template, request, jsonify, send_from_directory, session, flash, redirect, url_for
from data_logs import *
from datetime import datetime
import requests
import os

app = Flask(__name__)
app.secret_key = "ayfsdgkhoipdj"  # Needed for session & flash

# -----------------------
# Static Files
# -----------------------
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# -----------------------
# Login Route
# -----------------------
FIREBASE_SETTINGS_URL = "https://smart-bin-1b802-default-rtdb.asia-southeast1.firebasedatabase.app/settings.json"

def get_correct_pin():
    try:
        response = requests.get(FIREBASE_SETTINGS_URL)
        if response.status_code == 200:
            data = response.json()
            return data.get("CORRECT_PIN")  # Make sure your Firebase JSON has this key
        else:
            print("Failed to fetch PIN from Firebase:", response.status_code)
            return None
    except Exception as e:
        print("Error fetching PIN:", e)
        return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pin_inputs = request.form.getlist("pin")  # Get all 6 pin inputs
        pin = "".join(pin_inputs)

        correct_pin = get_correct_pin()
        if not correct_pin:
            flash("Unable to verify PIN at the moment.", "danger")
            return redirect(url_for("login"))

        if pin == correct_pin:
            session['logged_in'] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid PIN. Try again.", "danger")
            return redirect(url_for("login"))

    return render_template("index.html")

# -----------------------
# Logout Route
# -----------------------
@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

# -----------------------
# Protected Routes
# -----------------------
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# -----------------------
# API Routes
# -----------------------
@app.route('/getAllData')
@login_required
def getAllData():
    data = get_all_records()
    return jsonify(data)

@app.route('/getDashboardCount')
@login_required
def getDashboard():
    data = get_recycle_type_counts()
    return jsonify(data)

@app.route('/sendDataArduino', methods=['POST'])
@login_required
def sendDataArduino():
    input_data = request.form.get('data')
    
    if input_data and input_data != 'none':
        insert_data(input_data)
        return jsonify({'success': True, 'message': 'Data inserted successfully', 'data': input_data})
    else:
        return jsonify({'success': False, 'message': 'No valid data received'})

# -----------------------
# Run App
# -----------------------
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
