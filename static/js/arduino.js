let port;
let writer;

// Connect button click
document.getElementById("connect-btn").addEventListener("click", async () => {
  if (!("serial" in navigator)) {
    alert("Web Serial API not supported in this browser.");
    return;
  }

  try {
    // Prompt user to select a serial port
    port = await navigator.serial.requestPort();
    await port.open({ baudRate: 9600 });

    writer = port.writable.getWriter();
    console.log("Arduino connected!");
    $("#scanData").text("Arduino Connected!");
  } catch (err) {
    console.error("Error connecting to Arduino:", err);
    alert("Failed to connect to Arduino. Check USB connection.");
  }
});

// Modified sendData function
async function sendData(inputData) {
  if (inputData != "none") {
    $("#scanData").text(inputData);
  }

  setTimeout(() => {
    $("#scanData").text("Scanning...");
  }, 5000);

  // Send to Arduino if connected
  if (writer && port) {
    try {
      const encoder = new TextEncoder();
      await writer.write(encoder.encode(inputData + "\n"));
      console.log("Sent to Arduino:", inputData);
    } catch (err) {
      // console.error("Error sending to Arduino:", err);
      // alert("Failed to send data to Arduino.");
    }
  } else {
    console.warn("Arduino not connected. Click 'Connect Arduino' first.");
  }

  // Send to server via AJAX
  $.ajax({
    type: "POST",
    url: "/sendDataArduino",
    data: { data: inputData },
    dataType: "json",
    success: function (response) {
      console.log("Response from server:", response);
      if (response.success) {
        getAllData();
      } else {
        alert("Error sending data: " + response.message);
      }
    },
    error: function (xhr, status, error) {
      console.error("AJAX error:", status, error);
      alert("An error occurred while sending data.");
    },
  });
}
