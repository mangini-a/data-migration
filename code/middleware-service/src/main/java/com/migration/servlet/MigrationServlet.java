package com.migration.servlet;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import kong.unirest.HttpResponse;
import kong.unirest.Unirest;

@WebServlet("/migrate")
public class MigrationServlet extends HttpServlet {
    // Define service URLs as constants
    private static final String PHP_SERVICE_URL = "https://quizonline.altervista.org/second/public/api.php";
    private static final String PYTHON_SERVICE_URL = "http://localhost:5000/receive";

    // Create a Gson instance to be able to send JSON-formatted error responses to the client
    private final Gson gson = new Gson();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        // Set the response's content type and prepare an object that can send it
        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        // Get the table name of interest from request parameters
        String tableName = request.getParameter("table");

        // Validate the table name parameter
        if (tableName == null || tableName.trim().isEmpty()) {
            sendError(out, "Table name parameter is required.");
            return;
        }

        try {
            // Fetch data from the PHP web service
            String sourceData = fetchFromPhpService(tableName);

            // Forward the data to the Python web service
            String result = forwardToPythonService(sourceData);

            // Send its JSON-formatted response to the client
            out.write(result);

        } catch (Exception e) {
            sendError(out, "Error during migration: " + e.getMessage() + ".");
        }
    }

    /**
     * Fetches all the records belonging to the specified table from the remote database.
     * Uses HTTP GET to retrieve data from the PHP service.
     * 
     * @param tableName the name of the database table to be queried
     * @return the JSON data as a string
     * @throws IOException if there's an error in the HTTP communication
     */
    private String fetchFromPhpService(String tableName) throws IOException {
        HttpResponse<String> response = Unirest.get(PHP_SERVICE_URL)
                .queryString("table", tableName)
                .asString();

        if (response.getStatus() != 200) {
            throw new IOException("Failed to fetch data from PHP service: " + response.getStatusText());
        }

        return response.getBody();
    }

    /**
     * Forwards the data retrieved from the remote database to the local Python web service.
     * Uses HTTP POST to send the data.
     * 
     * @param sourceData the data retrieved from the remote database
     * @return the response from the Python service
     * @throws IOException if there's an error in the HTTP communication
     */
    private String forwardToPythonService(String sourceData) throws IOException {
        HttpResponse<String> response = Unirest.post(PYTHON_SERVICE_URL)
                .header("Content-Type", "application/json")
                .body(sourceData)
                .asString();

        if (response.getStatus() != 200) {
            throw new IOException("Failed to forward data to Python service: " + response.getStatusText());
        }

        return response.getBody();
    }

    /**
     * Sends an error response to the client in JSON format.
     * 
     * @param out the object that can send character text to the client
     * @param message the error message to be sent
     * @throws IOException if there's an error writing the response
     */
    private void sendError(PrintWriter out, String message) throws IOException {
        JsonObject error = new JsonObject();
        error.addProperty("status", "error");
        error.addProperty("message", message);
        out.write(gson.toJson(error));
    }
}
