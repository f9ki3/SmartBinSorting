function sendData(inputData) {
    $.ajax({
        type: "POST",
        url: "/sendDataArduino",  // URL to send the request to
        data: {'data': inputData}, // Data to send
        dataType: "json", // Expected data type from server
        success: function (response) {
            // Handle the success response from the server
            console.log("Response from server:", response);
            // Example: Do something with the response
            if (response.success) {
                alert("Data sent successfully!");
            } else {
                alert("Error sending data: " + response.message);
            }
        },
        error: function(xhr, status, error) {
            // Handle errors in case the request fails
            console.error("AJAX error:", status, error);
            alert("An error occurred while sending data.");
        }
    });
}
