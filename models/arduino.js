
let port;

// Function to connect to Arduino
async function connectToArduino() {
try {
    port = await navigator.serial.requestPort();  // Request serial port
    await port.open({ baudRate: 9600 });  // Open the serial port
    alert("Connected to Arduino!");
} catch (error) {
    console.error("Error connecting to Arduino:", error);
}
}

// Send message to Arduino
function sendToArduino(message) {
const writer = port.writable.getWriter();
const encoder = new TextEncoder();
writer.write(encoder.encode(message));
writer.releaseLock();
}

// Event listener for input
document.getElementById('inputText').addEventListener('input', function () {
const inputText = this.value.trim().toLowerCase();
if (inputText === "plastic") {
    sendToArduino("plastic");  // Send 'plastic' to Arduino when typed
}
});

// Connect button
document.getElementById('connectButton').addEventListener('click', connectToArduino);