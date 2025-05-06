from flask import Flask, render_template, request, jsonify, send_from_directory
import serial
import time
from data_logs import *
from datetime import datetime
import json
import os

app = Flask(__name__)

# Initialize serial communication with Arduino (change the port if necessary)
# arduino = serial.Serial('/dev/cu.usbserial-1430', 9600, timeout=1)  # Adjust port to match your Arduino or change COM3

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/')
def basuraHome():
    return render_template('index.html')

@app.route('/getAllData')
def getAllData():
    data = get_all_records()
    return jsonify(data)

@app.route('/getDashboardCount')
def getDashboard():
    data = get_recycle_type_counts()
    return jsonify(data)

DATA_FILE = os.path.join('static', 'data.json')

def read_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except:
        return {}

def write_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

@app.route('/send_data', methods=['POST'])
def send_data():
    try:
        data = request.get_json(force=True)

        stored_data = read_data()
        stored_data["sensor1"] = data.get("sensor1")
        stored_data["sensor2"] = data.get("sensor2")
        write_data(stored_data)

        return jsonify({"message": "Data from both sensors stored successfully!"}), 200

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400

    try:
        data = request.get_json(force=True)  # <-- force=True handles bad headers

        if not data or "distance" not in data:
            return jsonify({"message": "Missing or invalid JSON"}), 400

        stored_data = read_data()
        stored_data["distance"] = data["distance"]
        write_data(stored_data)

        return jsonify({"message": "Data received and stored successfully!"}), 200

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400
    

@app.route('/send_data2', methods=['POST'])
def send_data2():
    try:
        data = request.get_json(force=True)

        stored_data = read_data()
        stored_data["sensor3"] = data.get("sensor3")
        stored_data["sensor4"] = data.get("sensor4")
        write_data(stored_data)

        return jsonify({"message": "Data from sensors 3 and 4 stored successfully!"}), 200

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400



# Route to retrieve the stored data
@app.route('/retrieve_data', methods=['GET'])
def retrieve_data():
    try:
        # Read the stored data from the file
        data = read_data()

        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400

# @app.route('/sendDataArduino', methods=['POST'])
# def sendDataArduino():
#     input_data = request.form.get('data')  # Get data from the form (or AJAX)
#     if input_data:
#         # Send the data to Arduino via serial
#         arduino.write(input_data.encode())  # Send string to Arduino

#         # Wait for Arduino to process the data
#         time.sleep(2)  # Sleep for 2 seconds to allow Arduino to react
    
#         # Optionally, you can read response from Arduino (if needed)
#         response = arduino.readline().decode('utf-8').strip()

#         if input_data != 'none':
#             insert_data(input_data)

#         # Send a JSON response back to the client
#         return jsonify({'success': True, 'message': 'Data sent to Arduino', 'data': input_data, 'arduino_response': response})
#     else:
#         return jsonify({'success': False, 'message': 'No data received'})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
