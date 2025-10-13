from flask import Flask, render_template, request, jsonify, send_from_directory, session, flash, redirect, url_for
from data_logs import *
from datetime import datetime
import requests
import threading
import time
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
# Firebase URLs
# -----------------------
FIREBASE_SETTINGS_URL = "https://smart-bin-1b802-default-rtdb.asia-southeast1.firebasedatabase.app/settings.json"
FIREBASE_BINS_URL = "https://smart-bin-1b802-default-rtdb.asia-southeast1.firebasedatabase.app/bins.json"

previous_alerts = {}  # Store previous alert state to only alert on change

def get_bin_percentage(bin_cm, empty=25, full=5):
    """
    Convert sensor distance to fill percentage.
    - 25 cm = 0% full (empty)
    - 5 cm = 100% full
    - Linear mapping in between
    - Values above empty → 0%
    - Values below full → 100%
    """
    if bin_cm >= empty:
        return 0
    elif bin_cm <= full:
        return 100
    else:
        percent = ((empty - bin_cm) / (empty - full)) * 100
        return round(percent)

def check_bins_alert():
    global previous_alerts
    while True:
        try:
            # Fetch system notification setting
            settings_resp = requests.get(FIREBASE_SETTINGS_URL)
            notifications_enabled = False
            if settings_resp.status_code == 200:
                settings_data = settings_resp.json()
                notifications_enabled = settings_data.get("system-notification", False)

            if notifications_enabled:
                # Fetch bin data
                bins_resp = requests.get(FIREBASE_BINS_URL)
                if bins_resp.status_code == 200:
                    bins_data = bins_resp.json()
                    for bin_name in ["bin1", "bin2", "bin3", "bin4"]:
                        cm = bins_data.get(bin_name, 25)  # Default empty if missing
                        percent = get_bin_percentage(cm)
                        alert_type = None

                        if percent >= 100:
                            alert_type = "full"
                        elif percent >= 80:
                            alert_type = "almost full"

                        # Print percentage for each bin
                        print(f"{bin_name}: {percent}% full")

                        # Only alert if state changed
                        if previous_alerts.get(bin_name) != alert_type and alert_type:
                            print(f"ALERT: {bin_name} is {alert_type} ({percent}%)")
                            previous_alerts[bin_name] = alert_type

                            # Increment settings.notification in Firebase
                            try:
                                current_notification_count = settings_data.get("notification", 0)
                                updated_count = current_notification_count + 1
                                requests.patch(FIREBASE_SETTINGS_URL, json={"notification": updated_count})
                                print(f"Updated notification count to {updated_count}")
                            except Exception as e:
                                print("Failed to update notification count:", e)
                        elif alert_type is None:
                            previous_alerts[bin_name] = None

        except Exception as e:
            print("Error checking bins:", e)

        time.sleep(10)  # check every 10 seconds


def start_alert_thread():
    thread = threading.Thread(target=check_bins_alert)
    thread.daemon = True
    thread.start()


def get_correct_pin():
    try:
        response = requests.get(FIREBASE_SETTINGS_URL)
        if response.status_code == 200:
            data = response.json()
            return data.get("password")  # Make sure your Firebase JSON has this key
        else:
            print("Failed to fetch PIN from Firebase:", response.status_code)
            return None
    except Exception as e:
        print("Error fetching PIN:", e)
        return None

@app.route('/reset_notification_count', methods=['POST'])
def reset_notification_count():
    try:
        # Reset notification to 0
        requests.patch(FIREBASE_SETTINGS_URL, json={"notification": 0})
        return jsonify({"success": True})
    except Exception as e:
        print("Failed to reset notification count:", e)
        return jsonify({"success": False}), 500
    
@app.route('/get_notification_count')
def get_notifications_count():
    try:
        resp = requests.get(FIREBASE_SETTINGS_URL)
        if resp.status_code == 200:
            data = resp.json()
            count = data.get("notification", 0)
            return jsonify({'count': count})
        else:
            return jsonify({'count': 0})
    except Exception as e:
        print("Error fetching notification count:", e)
        return jsonify({'count': 0})
    
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
    if session.get('logged_in'):
        # User is already logged in, redirect to dashboard
        return redirect(url_for('dashboard'))
    # Otherwise, show the login page
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

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
    start_alert_thread() 
    app.run(debug=True, host='0.0.0.0', port=5000)
