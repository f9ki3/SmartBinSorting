from flask import Flask, render_template, request, jsonify
import serial
import time

app = Flask(__name__)

# Initialize serial communication with Arduino (change the port if necessary)
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Adjust port to match your Arduino or change COM3

@app.route('/')
def basuraHome():
    return render_template('index.html')

@app.route('/sendDataArduino', methods=['POST'])
def sendDataArduino():
    input_data = request.form.get('data')  # Get data from the form (or AJAX)
    
    if input_data:
        # Send the data to Arduino via serial
        arduino.write(input_data.encode())  # Send string to Arduino

        # Wait for Arduino to process the data
        time.sleep(2)  # Sleep for 2 seconds to allow Arduino to react

        # Optionally, you can read response from Arduino (if needed)
        response = arduino.readline().decode('utf-8').strip()

        # Send a JSON response back to the client
        return jsonify({'success': True, 'message': 'Data sent to Arduino', 'data': input_data, 'arduino_response': response})
    else:
        return jsonify({'success': False, 'message': 'No data received'})

if __name__ == "__main__":
    app.run(debug=True)
