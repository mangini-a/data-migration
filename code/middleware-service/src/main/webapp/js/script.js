$(document).ready(function() {
    fetchTables();
    generateCopyright();
});

/**
 * Retrieves the list of tables from the remote database using the Fetch API.
 * Creates interactive buttons for each table in the response.
*/
async function fetchTables() {
    // Get references to DOM elements which will/could be updated
    const $tableContainer = $("#table-container");
    const $message = $("#message");

    const url = "https://quizonline.altervista.org/second/public/fetch_tables.php";
    try {
        // Make the request to the PHP service
        const response = await fetch(url, {
            headers: {
                "Accept": "application/json"
            }
        });

        // Check if the response was successful
        if (!response.ok) {
            // Handle HTTP errors (like 404, 500, etc.)
            throw new Error(`HTTP error! Response status: ${response.status}`);
        }

        // Parse the JSON response
        const json = await response.json();

        if (json.status === "success") {
            // Clear existing content before adding new buttons
            $tableContainer.empty();

            // Create buttons for each table
            json.tables.forEach(function(table) {
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
            .text("Failed to fetch tables: " + (json.message || "Unknown error."));
        }

    } catch (error) {
        // Construct an appropriate error message based on the error
        let errorMessage = "Error fetching tables: ";

        if (!navigator.onLine) {
            // Check if the user is offline
            errorMessage += "could not connect to the server. Please check your internet connection.";
        } else if (error instanceof TypeError) {
            // Network errors like CORS or offline result in TypeError
            errorMessage += "could not connect to the server. Please try again.";
        } else {
            // For all other errors, use the error message
            errorMessage += error.message;
        }

        $message.removeClass().addClass("error").text(errorMessage);
        console.error("Error details:", error);
    }
}

/**
 * Makes a GET request to the servlet using the Fetch API.
 * Updates the UI to show progress and results of the migration.
 * 
 * @param {String} tableName the name of the table to be migrated
 */
async function makeGetRequest(tableName) {
    // Get references to DOM elements which will be updated
    const $message = $("#message");
    const $button = $(`button:contains('${tableName}')`);

    // Disable the button and show loading state during migration
    $button.prop("disabled", true);
    $message.removeClass().addClass("loading")
        .text(`Migrating ${tableName}'s data... Please wait.`);

    const url = `migrate?table=${encodeURIComponent(tableName)}`;
    try {
        // Make the request to the servlet
        const response = await fetch(url, {
            headers: {
                "Accept": "application/json"
            }
        });

        // Check if the response was successful
        if (!response.ok) {
            // Handle different HTTP error status codes
            if (response.status === 400) {
                throw new Error("the request could not be understood. Make sure the Python server is running.");
            } else if (response.status === 404) {
                throw new Error("migration servlet not found. Please check your server configuration.");
            } else if (response.status === 500) {
                throw new Error("server error during migration.");
            } else {
                throw new Error(`HTTP error! Response status: ${response.status}`);
            }
        }

        // Parse the JSON response
        const json = await response.json();

        // Update UI based on response status
        if (data.status === "success") {
            $message.removeClass().addClass("success").text(data.message);
        } else {
            $message.removeClass().addClass("error")
                .text(data.message || "Unknown error occurred.");
        }

    } catch (error) {
        // Construct an appropriate error message based on the error
        let errorMessage = "Error occurred: ";

        if (!navigator.onLine) {
            // Check if the user is offline
            errorMessage += "connection was aborted. Please check your internet connection.";
        } else if (error instanceof TypeError) {
            // Network errors result in TypeError
            errorMessage += "connection was aborted. Please try again.";
        } else {
            // For all other errors, use the error message
            errorMessage += error.message;
        }

        $message.removeClass().addClass("error").text(errorMessage);
        console.error("Migration error:", error);

    } finally {
        // Re-enable the button regardless of success/failure
        $button.prop("disabled", false);
    }
}

function generateCopyright() {
    $(".copyright").html("<p>&copy; " + getCurrentYear() + " Alessandro Mangini. All rights reserved.</p>");
}

function getCurrentYear() {
    return new Date().getFullYear();
}
