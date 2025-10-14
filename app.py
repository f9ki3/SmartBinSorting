# app.py
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

BIN_MAPPING = {
    "bin1": "paper bin",
    "bin2": "general bin",
    "bin3": "plastic bin",
    "bin4": "metal bin"
}

# -----------------------
# Helpers
# -----------------------
def get_bin_percentage(cm):
    MAX_HEIGHT = 25
    try:
        percent = 100 - int((cm / MAX_HEIGHT) * 100)
    except Exception:
        percent = 0
    return max(0, min(100, percent))

def log_notification(friendly_name, alert_type, percent):
    print(f"[NOTIFY] {friendly_name} is {alert_type.upper()} ({percent}%)")

def send_sms_alert(message, phone_number):
    """Send SMS alert using iprogtech API"""
    try:
        payload = {"message": message, "phone_number": phone_number}
        headers = {"Content-Type": "application/json"}
        url = f"{SMS_API_URL}?api_token={SMS_API_TOKEN}"
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            print(f"[SMS] Sent to {phone_number}: {message}")
        else:
            print(f"[SMS] Failed ({resp.status_code}): {resp.text}")
    except Exception as e:
        print("[SMS] Error sending SMS:", e)

# -----------------------
# Background monitoring loop
# -----------------------
def check_bins_alert():
    global previous_alerts
    print("✅ Smart Bin monitor thread started (pid: {})".format(os.getpid()))

    while True:
        try:
            # Fetch system settings
            settings_resp = requests.get(FIREBASE_SETTINGS_URL, timeout=8)
            notifications_enabled = False
            sms_enabled = False
            settings_data = {}

            if settings_resp.status_code == 200:
                settings_data = settings_resp.json() or {}
                notifications_enabled = settings_data.get("system-notification", False)
                sms_enabled = settings_data.get("sms-notification", False)

            if notifications_enabled:
                bins_resp = requests.get(FIREBASE_BINS_URL, timeout=8)
                if bins_resp.status_code == 200:
                    bins_data = bins_resp.json() or {}

                    for raw_bin, friendly_name in BIN_MAPPING.items():
                        cm = bins_data.get(raw_bin, 25)
                        percent = get_bin_percentage(cm)
                        alert_type = None

                        if percent >= 100:
                            alert_type = "full"
                        elif percent >= 80:
                            alert_type = "almost full"

                        # Only alert on state change and when there is an alert
                        if previous_alerts.get(friendly_name) != alert_type and alert_type:
                            previous_alerts[friendly_name] = alert_type

                            # Log the notification
                            log_notification(friendly_name, alert_type, percent)

                            # Increment Firebase notification counter
                            try:
                                current_count = settings_data.get("notification", 0) or 0
                                updated_count = current_count + 1
                                requests.patch(FIREBASE_SETTINGS_URL, json={"notification": updated_count}, timeout=8)
                                print(f"[FIREBASE] Updated notification count to {updated_count}")
                            except Exception as e:
                                print("[FIREBASE] Failed to update notification count:", e)

                            # Send SMS if enabled
                            if sms_enabled:
                                try:
                                    sms_resp = requests.get(FIREBASE_SMS_URL, timeout=8)
                                    if sms_resp.status_code == 200:
                                        phone_data = sms_resp.json() or {}
                                        phone_number = phone_data.get("phone")
                                        if phone_number:
                                            msg = f"Smart Waste Management Alerts: {friendly_name} is {alert_type.upper()} ({percent}%)"
                                            send_sms_alert(msg, phone_number)
                                        else:
                                            print("[SMS] No phone number found in Firebase.")
                                except Exception as e:
                                    print("[SMS] Error fetching phone number:", e)

                        elif alert_type is None:
                            previous_alerts[friendly_name] = None

        except Exception as e:
            print("[Monitor] Error checking bins:", e)

        # Sleep between checks (adjust as needed)
        time.sleep(3)

# -----------------------
# Thread startup control (one per process)
# -----------------------
thread_started = False
thread_lock = threading.Lock()

def start_alert_thread():
    """Start the monitoring thread (daemon). Safe to call multiple times."""
    global thread_started
    with thread_lock:
        if thread_started:
            return
        thread = threading.Thread(target=check_bins_alert, name="smart-bin-monitor", daemon=True)
        thread.start()
        thread_started = True
        print("[Thread] Alert thread launched (daemon=True) in pid:", os.getpid())

# Ensure thread starts when the module is imported (renders & gunicorn import app)
# This will start one thread per process — which is typically what you want with Gunicorn worker processes.
try:
    start_alert_thread()
except Exception as e:
    print("[Thread] Failed to start at import:", e)

# Also ensure thread is activated before first request if for some reason import-time start didn't happen
@app.before_first_request
def ensure_thread_running():
    start_alert_thread()

# -----------------------
# Routes & APIs
# -----------------------
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/reset_notification_count', methods=['POST'])
def reset_notification_count():
    try:
        requests.patch(FIREBASE_SETTINGS_URL, json={"notification": 0}, timeout=8)
        return jsonify({"success": True})
    except Exception as e:
        print("Failed to reset notification count:", e)
        return jsonify({"success": False}), 500

@app.route('/get_notification_count')
def get_notifications_count():
    try:
        resp = requests.get(FIREBASE_SETTINGS_URL, timeout=8)
        if resp.status_code == 200:
            data = resp.json() or {}
            count = data.get("notification", 0) or 0
            return jsonify({'count': count})
    except Exception as e:
        print("Error fetching notification count:", e)
    return jsonify({'count': 0})

@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 10))

    try:
        resp = requests.get(FIREBASE_NOTIF_URL, timeout=8)
        if resp.status_code != 200:
            return jsonify([])

        data = resp.json() or {}
        if not data:
            return jsonify([])

        notifications = sorted(
            [{"id": k, **v} for k, v in data.items()],
            key=lambda x: x.get("timestamp", 0),
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
        pin_inputs = request.form.getlist("pin")
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

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

# login_required decorator
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
def index_route():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
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

@app.route('/getAllData')
@login_required
def getAllData_route():
    data = get_all_records()
    return jsonify(data)

@app.route('/getDashboardCount')
@login_required
def getDashboard_route():
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

def get_correct_pin():
    try:
        response = requests.get(FIREBASE_SETTINGS_URL, timeout=8)
        if response.status_code == 200:
            data = response.json() or {}
            return data.get("password")
    except Exception as e:
        print("Error fetching PIN:", e)
    return None

# -----------------------
# Local run (useful for development)
# -----------------------
if __name__ == "__main__":
    # This will start thread again in local run (start_alert_thread is idempotent)
    print("🚀 Running locally (debug mode). PID:", os.getpid())
    start_alert_thread()
    app.run(debug=True, host='0.0.0.0', port=5000)
