$(document).ready(function() {
    fetchTables();
});

/**
 * Retrieves the list of tables from the remote database by means of an ad hoc PHP script.
 * Creates a button for each table, which when clicked makes a GET request to the servlet.
 */
function fetchTables() {
    fetch("https://quizonline.altervista.org/second/public/fetch_tables.php")
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                const tableContainer = $("#table-container");
                tableContainer.html("");
                data.tables.forEach(table => {
                    const button = document.createElement("button");
                    button.text(table);
                    button.on("click", makeGetRequest(table));
                    button.appendTo(tableContainer);
                });
            } else {
                alert("Failed to fetch tables: " + data.message);
            }
        })
        .catch(error => {
            alert("Error fetching tables: " + error);
        });
}

/**
 * Makes a GET request to the servlet.
 * 
 * @param {String} tableName the name of the table to be migrated
 */
function makeGetRequest(tableName) {
    fetch("http://localhost:8080/middleware-service-1.0-SNAPSHOT/migrate?table=" + tableName);
}
