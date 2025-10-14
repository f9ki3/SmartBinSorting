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
FIREBASE_NOTIF_URL = "https://smart-bin-1b802-default-rtdb.asia-southeast1.firebasedatabase.app/notifications.json"
FIREBASE_SMS_URL = "https://smart-bin-1b802-default-rtdb.asia-southeast1.firebasedatabase.app/sms-number.json"

# SMS API
SMS_API_URL = "https://sms.iprogtech.com/api/v1/sms_messages"
SMS_API_TOKEN = "3c0ca3aa1015545b917440f1b6418d429fe56f0c"

previous_alerts = {}  # Store previous alert state to only alert on change

def get_bin_percentage(cm):
    # Example logic
    MAX_HEIGHT = 25
    percent = 100 - int((cm / MAX_HEIGHT) * 100)
    return max(0, min(100, percent))

def log_notification(friendly_name, alert_type, percent):
    print(f"LOG: {friendly_name} is {alert_type.upper()} ({percent}%)")
        
BIN_MAPPING = {
    "bin1": "paper bin",
    "bin2": "general bin",
    "bin3": "plastic bin",
    "bin4": "metal bin"
}

def send_sms_alert(message, phone_number):
    """Send SMS alert using iprogtech API"""
    try:
        payload = {
            "message": message,
            "phone_number": phone_number
        }
        headers = {"Content-Type": "application/json"}
        url = f"{SMS_API_URL}?api_token={SMS_API_TOKEN}"
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            print(f"SMS sent to {phone_number}: {message}")
        else:
            print(f"Failed to send SMS ({resp.status_code}): {resp.text}")
    except Exception as e:
        print("❌ Error sending SMS:", e)


def check_bins_alert():
    global previous_alerts

    while True:
        try:
            # Fetch system settings
            settings_resp = requests.get(FIREBASE_SETTINGS_URL)
            notifications_enabled = False
            sms_enabled = False
            settings_data = {}

            if settings_resp.status_code == 200:
                settings_data = settings_resp.json()
                notifications_enabled = settings_data.get("system-notification", False)
                sms_enabled = settings_data.get("sms-notification", False)

            if notifications_enabled:
                bins_resp = requests.get(FIREBASE_BINS_URL)
                if bins_resp.status_code == 200:
                    bins_data = bins_resp.json()

                    for raw_bin, friendly_name in BIN_MAPPING.items():
                        cm = bins_data.get(raw_bin, 25)
                        percent = get_bin_percentage(cm)
                        alert_type = None

                        if percent >= 100:
                            alert_type = "full"
                        elif percent >= 80:
                            alert_type = "almost full"

                        # Only alert if state changed
                        if previous_alerts.get(friendly_name) != alert_type and alert_type:
                            previous_alerts[friendly_name] = alert_type

                            # Log the notification
                            log_notification(friendly_name, alert_type, percent)

                            # Increment Firebase notification counter
                            try:
                                current_count = settings_data.get("notification", 0)
                                updated_count = current_count + 1
                                requests.patch(FIREBASE_SETTINGS_URL, json={"notification": updated_count})
                                print(f"Updated notification count to {updated_count}")
                            except Exception as e:
                                print("Failed to update notification count:", e)

                            # ---- SEND SMS ALERT ----
                            if sms_enabled:
                                try:
                                    sms_resp = requests.get(FIREBASE_SMS_URL)
                                    if sms_resp.status_code == 200:
                                        phone_data = sms_resp.json()
                                        phone_number = phone_data.get("phone")

                                        if phone_number:
                                            msg = f" Smart Waste Management Alerts: {friendly_name} is {alert_type.upper()} ({percent}%)"
                                            send_sms_alert(msg, phone_number)
                                        else:
                                            print("No phone number found in Firebase.")
                                except Exception as e:
                                    print("Error fetching phone number:", e)

                        elif alert_type is None:
                            previous_alerts[friendly_name] = None

        except Exception as e:
            print("Error checking bins:", e)

        time.sleep(3)

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

@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    """
    Returns notifications in batches for lazy loading.
    Query params:
      start: index to start
      limit: number of notifications
    """
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 10))

    try:
        resp = requests.get(FIREBASE_NOTIF_URL)
        if resp.status_code != 200:
            return jsonify([])

        data = resp.json()
        if not data:
            return jsonify([])

        # Convert object to list and sort by timestamp descending
        notifications = sorted(
            [{"id": k, **v} for k, v in data.items()],
            key=lambda x: x["timestamp"],
            reverse=True
        )

        batch = notifications[start:start+limit]
        return jsonify(batch)
    except Exception as e:
        print("Failed to fetch notifications:", e)
        return jsonify([])

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
    # Only start the thread once when using debug/reloader
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_alert_thread() 
    # app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=False)


