$(document).ready(function() {
    fetchTables();
});

/**
 * Retrieves the list of tables from the remote database by means of an ad hoc PHP script.
 * Creates a button for each table, which when clicked makes a GET request to the servlet.
*/
function fetchTables() {
    // Get references to DOM elements which will/could be updated
    const $tableContainer = $("#table-container");
    const $message = $("#message");

    // Make the AJAX request using jQuery (15-second timeout)
    $.ajax({
        url: "https://quizonline.altervista.org/second/public/fetch_tables.php",
        dataType: "json",
        timeout: 15000,
        success: function(data) {
            if (data.status === "success") {
                // Clear existing content before adding new buttons
                $tableContainer.empty();

                // Create buttons for each table
                data.tables.forEach(function(table) {
                    $("<button>")
                        .text(table)
                        .on("click", function() {
                            makeGetRequest(table);
                        })
                        .appendTo($tableContainer);
                });
            } else {
                // Handle API success but with error status
                $message.text("Failed to fetch tables: " + (data.message || "Unknown error."))
                    .css("color", "darkred");
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            // Construct a meaningful error message based on the type of error
            let errorMessage = "Error fetching tables: ";
            
            // Consider a number of relevant scenarios
            if (textStatus === "timeout") {
                errorMessage += "request timed out. Please try again.";
            } else if (jqXHR.status === 0) {
                errorMessage += "could not connect to the server. Please check your internet connection.";
            } else if (jqXHR.status === 404) {
                errorMessage += "the requested resource was not found.";
            } else if (jqXHR.status === 500) {
                errorMessage += "internal server error occurred.";
            } else {
                errorMessage += `${textStatus} - ${errorThrown}`;
            }
            
            // Display the error message
            $message.text(errorMessage).css("color", "darkred");
            
            // Log the error details for debugging
            console.error("Error details:", {
                status: jqXHR.status,
                textStatus: textStatus,
                errorThrown: errorThrown
            });
        }
    });
}

/**
 * Makes a GET request to the servlet and handles its JSON-formatted response.
 * 
 * @param {String} tableName the name of the table to be migrated
 */
function makeGetRequest(tableName) {
    // Show the user that the data transfer operation is in progress
    const $message = $("#message");
    $message.text(`Migrating ${tableName}'s data...`).css("color", "#555");

    // Perform an asynchronous HTTP GET request to the servlet (60-second timeout)
    $.ajax({
        url: "/middleware-service-1.0-SNAPSHOT/migrate",
        data: {
          table: tableName
        },
        dataType: "json",
        timeout: 60000,
        success: function(data) {
            if (data.status === "success") {
                $message.text(data.message).css("color", "#555");
            } else {
                $message.text(data.message || "Unknown error occurred.").css("color", "darkred");
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            // Construct a meaningful error message based on the type of error
            let errorMessage = "Error occurred: ";

            // Consider a number of relevant scenarios
            if (jqXHR.status === 400) {
                errorMessage += "the request could not be understood. Make sure the Python server is running.";
            } else if (jqXHR.status === 404) {
                errorMessage += "migration servlet not found. Please check your server configuration.";
            } else if (jqXHR.status === 500) {
                errorMessage += "server error during migration.";
            } else if (textStatus === "timeout") {
                errorMessage += "request timed out. The operation might still be processing.";
            } else {
                errorMessage += `${textStatus} - ${errorThrown}`;
            }

            // Display the error message
            $message.text(errorMessage).css("color", "darkred");

            // Log the error details for debugging
            console.error("Migration error:", {
                status: jqXHR.status,
                textStatus: textStatus,
                errorThrown: errorThrown
            });
        }
    });
}
