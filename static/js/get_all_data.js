function getAllData() {
  $.ajax({
    type: "GET",
    url: "/getAllData", // Flask route to get data
    dataType: "json", // Expect JSON response from the server
    success: function (response) {
      // Clear existing table rows
      $("#dataLogs").empty();

      // Loop through the response and append rows
      response.forEach((item) => {
        const row = `
                    <tr>
                        <td style="width: 50%;" class="pb-2 pt-2">${item.timestamp}</td>
                        <td style="width: 50%;" class="pb-2 pt-2">${item.recycle_type}</td>
                    </tr>
                `;
        $("#dataLogs").append(row);
      });
    },
    error: function (xhr, status, error) {
      console.error("Error fetching data:", error);
    },
  });
}

// Call the function to populate data on page load
getAllData();
