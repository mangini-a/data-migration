$(document).ready(function() {
    fetchTables();
    generateCopyright();
});

/**
 * Retrieves the list of tables from the remote database by means of an ad hoc PHP script.
 * Creates a button for each table, which when clicked makes a GET request to the servlet.
*/
function fetchTables() {
    // Get references to DOM elements which will/could be updated
    const $tableContainer = $("#table-container");
    const $message = $("#message");

    // Perform an asynchronous HTTP GET request to the PHP script (15-second timeout)
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
                $message.removeClass().addClass("error")
                .text("Failed to fetch tables: " + (data.message || "Unknown error."));
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            let errorMessage = "Error fetching tables: ";
            
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
            
            $message.removeClass().addClass("error").text(errorMessage);
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
    // Get references to DOM elements which will be updated
    const $message = $("#message");
    const $button = $(`button:contains('${tableName}')`);

    // Disable the button and show loading state during migration
    $button.prop("disabled", true);
    $message.removeClass().addClass("loading")
        .text(`Migrating ${tableName}'s data... Please wait.`);

    // Perform an asynchronous HTTP GET request to the servlet (2-minute timeout)
    $.ajax({
        url: "migrate",
        data: {
          table: tableName
        },
        dataType: "json",
        timeout: 120000,
        success: function(data) {
            if (data.status === "success") {
                $message.removeClass().addClass("success").text(data.message);
            } else {
                $message.removeClass().addClass("error")
                    .text(data.message || "Unknown error occurred.");
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            let errorMessage = "Error occurred: ";

            if (jqXHR.status === 0 && textStatus !== "timeout") {
                errorMessage += "connection was aborted. Please try again."
            } else if (jqXHR.status === 400) {
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

            $message.removeClass().addClass("error").text(errorMessage);
            console.error("Migration error:", {
                status: jqXHR.status,
                textStatus: textStatus,
                errorThrown: errorThrown
            });
        },
        complete: function() {
            // Re-enable the button regardless of success/failure
            $button.prop("disabled", false);
        }
    });
}

function generateCopyright() {
    $(".copyright").html("<p>&copy; " + getCurrentYear() + " Alessandro Mangini. All rights reserved.</p>");
}

function getCurrentYear() {
    return new Date().getFullYear();
}
